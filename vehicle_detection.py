import os
import cv2
from PIL import Image
import glob
from statistics import median


def get_frame_number(elem: str) -> int:  # функция для вычленения номера фрейма, используем для сортировки
    return int(elem.replace('frame', '').replace('.png', ''))


def click_event(event, x, y, flags, params):
    global x_click, y_click, rect_x, rect_y, num_square
    # img_file = 'greyscale.png'
    # gray_img = cv2.imread(img_file, cv2.IMREAD_GRAYSCALE)  # grayscale
    if event == cv2.EVENT_LBUTTONDOWN:
        if num_square > 4:
            print('maximum num of square')
            cv2.destroyAllWindows()
        else:
            rect_x.append(x)
            rect_y.append(y)
            print('x =', x, ' ', 'y =', y)
            x_click = x
            y_click = y

            rect_image = cv2.rectangle(gray_img, (x - radius, y - radius), (x + radius, y + radius), (255, 0, 0), 1)
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(rect_image, 'det' + str(num_square) + ':' + str(x) + ',' +
                        str(y), (x + radius +2, y), font,
                        0.5, (255, 255, 255), 1)
            cv2.imshow('Image with rectangle', rect_image)

            grey_for_mid_color_images_unsorted = os.listdir('frames')
            grey_for_mid_color_images = sorted(grey_for_mid_color_images_unsorted, key=get_frame_number)
            temp_list_coments = []
            if num_square == 1:
                list_mid_color.append('Детектор 1 ' + '[' + str(x) + ',' + str(y) + '] ' + comentForFirst)
            elif num_square == 2:
                list_mid_color.append('Детектор 2 ' + '[' + str(x) + ',' + str(y) + '] ' + comentForSecond)
            elif num_square == 3:
                list_mid_color.append('Детектор 3 ' + '[' + str(x) + ',' + str(y) + '] ' + comentForThird)
            elif num_square == 4:
                list_mid_color.append('Детектор 4 ' + '[' + str(x) + ',' + str(y) + '] ' + comentForFourth)
            temp_list_mid_color = []
            for mid_color_img in grey_for_mid_color_images:

                img = cv2.imread('frames/%s' % mid_color_img, cv2.IMREAD_GRAYSCALE)
                colors_sum = 0
                for x_pix in range(x_click - radius, x_click + radius):
                    for y_pix in range(y_click - radius, y_click + radius):
                        colors_sum += img[y_pix, x_pix]
                mid_color = round(colors_sum / (4 * radius * radius), 2)
                temp_list_mid_color.append(mid_color)

                # print(img)
            list_mid_color.append(temp_list_mid_color)

            num_square += 1
    if event == cv2.EVENT_RBUTTONUP:
        cv2.destroyAllWindows()


x_click = 0
y_click = 0
rect_x = []  # массив х-координат мест, куда пользователь ставил квадраты (клики)
rect_y = []
num_square = 1
list_mid_color = []
vidcap = cv2.VideoCapture('dom10.avi')
fps = vidcap.get(cv2.CAP_PROP_FPS)
frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = frame_count / fps

print('fps = ' + str(fps))
print('number of frames = ' + str(frame_count))
print('duration (S) = ' + str(duration))
minutes = int(duration / 60)
seconds = duration % 60
print('duration (M:S) = ' + str(minutes) + ':' + str(seconds))

step = int(input('Введите шаг чтения кадров = '))
radius = int(input('Введите радиус ячейки = '))

comentForFirst = str(input('Введите комментарий для первого детектора:'))
comentForSecond = str(input('Введите комментарий для второго детектора:'))
comentForThird= str(input('Введите комментарий для третьего детектора:'))
comentForFourth = str(input('Введите комментарий для четвертого детектора:'))
success, image = vidcap.read()
count = 0
if success:
    cv2.imwrite('frames/frame_%d.png' % count, image)
    count += 1
while success:
    success, image = vidcap.read()
    if (count % step == 0) and (success):
        cv2.imwrite('frames/frame_%d.png' % count, image)  # save frame as JPEG file
        print('Read a new frame: ', success)
    count += 1
vidcap.release()  # освобождаем память

rgb_images = os.listdir('frames')  # получаем список всех rgb изображений в папке
for rgb_img in rgb_images:  # в цикле сохраняем все цветные изображения чёрно-белыми
    img = Image.open('frames/%s' % rgb_img).convert('LA')
    img.save('frames/%s' % rgb_img.replace('_', ''))
    os.remove('frames/%s' % rgb_img)  # удаляем поочерёдно rgb изображения

gray_img = cv2.imread('frames/frame0.png', cv2.IMREAD_GRAYSCALE)  # grayscale
font = cv2.FONT_HERSHEY_SIMPLEX
cv2.putText(gray_img, '1', (35, 200), font,
            0.5, (255, 0, 0), 1)
cv2.putText(gray_img, '2', (90, 200), font,
            0.5, (255, 0, 0), 1)
cv2.putText(gray_img, '3', (230, 200), font,
            0.5, (255, 0, 0), 1)
cv2.putText(gray_img, '4', (285, 200), font,
            0.5, (255, 0, 0), 1)
cv2.imshow('Select region', gray_img)

cv2.setMouseCallback('Select region', click_event)
cv2.waitKey(0)

print(list_mid_color)

object_binary_list = []	# список, определяющий наличие объекта в детекторе (0 или 1)
for i in range(1, len(list_mid_color), 2):  # берём только списки цветов
	object_binary_temp = []
	detection_list = list_mid_color[i]
	for det_color in detection_list:
		if abs(det_color - median(detection_list)) / median(detection_list) > 0.04:	# порог допущения 4%, если отличие в цвете меньше, то это считается погрешностью камеры
			object_binary_temp.append(1)
		else:
			object_binary_temp.append(0)
	object_binary_list.append(object_binary_temp)
with open('mid_color.txt', 'w') as f:
    for item in list_mid_color:
        f.write("%s\n" % item)
all_frames = glob.glob('frames/*')  # удаляем все фреймы из папки
for f in all_frames:
    os.remove(f)
