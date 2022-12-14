import time
from datetime import datetime
import re
import json
from selenium.webdriver.common.by import By
import selenium.common.exceptions
import driver_pikabu


def url_pars(url):
    driver = driver_pikabu.driver_start()
    start_time = time.time()
    try:
        driver.get(url)
    except selenium.common.exceptions.TimeoutException:
        try:
            driver_pikabu.driver_end(driver)
            driver = driver_pikabu.driver_with_proxy()
            driver.get(url)
        except selenium.common.exceptions.TimeoutException:
            return
    # Создание дополнительной вкладки для работы
    main_page = driver.current_window_handle
    driver.switch_to.new_window()
    sec_page = driver.current_window_handle
    driver.switch_to.window(main_page)
    # Ожидание Cloudflare
    time.sleep(3)
    #
    file_name = 'results/result_' + str(datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M')) + '.txt'
    pages_count = driver.find_element(By.CSS_SELECTOR, '.stories-feed').get_attribute('data-page-last')
    pages_count = int(pages_count)
    url_stat = "https://pikabu.ru/stat/story/"
    story_list = []
    # Перебор страниц
    # debug
    #pages_count = 5
    # debug
    print("[START] Pages count: ", pages_count)
    for i in range(1, pages_count):
        print(f"{i}/{pages_count}")
        try:
            driver.get(url)
        except selenium.common.exceptions.TimeoutException:
            try:
                driver_pikabu.driver_end(driver)
                driver = driver_pikabu.driver_with_proxy()
                driver.get(url + "?page=" + str(i))
            except selenium.common.exceptions.TimeoutException:
                return
        # Прогрузка данных последней статьи
        last_story = driver.find_element(By.CLASS_NAME, 'last-story')
        last_story.location_once_scrolled_into_view
        time.sleep(0.2)
        last_story = last_story.get_attribute('data-story-id')
        # Работа со статьями
        stories = driver.find_elements(By.CLASS_NAME, 'story')
        time.sleep(1)
        for story in stories:
            # Проверка рекламы
            if check_sponsor(story):
                continue
            # Проверка правильности найденной статьи
            try:
                st_title = story.find_element(By.CSS_SELECTOR, '.story__title-link')
                st_link = st_title.get_attribute('href')
            except:
                continue
            # Сбор тегов
            tags_lib = []
            st_user = story.find_element(By.CSS_SELECTOR, '.story__user-link.user__nick').get_attribute('data-name')
            try:
                hint_tags = story.find_element(By.CSS_SELECTOR, '.tags-cut')
                hint_tags.click()
            except:
                pass
            for tag in story.find_elements(By.CSS_SELECTOR, '.story__tags.tags > .tags__tag'):
                tags_lib.append(tag.text)
            # Сбор основных метаданных
            try:
                story.find_element(By.CSS_SELECTOR, '.story__author-panel')
                st_author = True
            except:
                st_author = False
            st_id = story.get_attribute('data-story-id')
            st_user_id = story.get_attribute('data-author-id')
            st_user_link = story.find_element(By.CSS_SELECTOR, '.story__user-link.user__nick').get_attribute('href')
            st_comm = story.get_attribute('data-comments')
            # Сбор просмотров
            driver.switch_to.window(sec_page)
            driver.get(url_stat + st_id)
            st_views = driver.find_element(By.CSS_SELECTOR, "body > pre").text
            st_views = re.search(r'(v\":)(\d+)', st_views)[2]
            driver.switch_to.window(main_page)
            #
            st_download = story.find_element(By.CSS_SELECTOR, '.story__save.hint').get_attribute('aria-label')
            st_rating = story.get_attribute('data-rating')
            try:
                st_time = story.find_element(By.CSS_SELECTOR,
                                             '.story__main > header > div > div > div > time').get_attribute('datetime')
            except:
                st_time = story.find_element(By.CSS_SELECTOR,
                                             '.caption.story__datetime.hint').get_attribute('datetime')
                driver.save_screenshot(st_id + ".png")
            content = get_content(story)
            # Сбор контента при неудачной попытке
            if not content:
                driver.switch_to.window(sec_page)
                driver.get(st_link)
                time.sleep(1)
                story_sec = driver.find_element(By.CLASS_NAME, 'story')
                content = get_content(story_sec)
                driver.switch_to.window(main_page)
            #
            story_item = {
                'story_id': st_id,
                'user': st_user,
                'user_id': st_user_id,
                'user_link': st_user_link,
                'title': st_title.text,
                'link': st_link,
                'comments count': st_comm,
                'views count': re.sub(r'[^0-9]+', r'', st_views),
                'downloads': re.sub(r'[^0-9]+', r'', st_download),
                'rating': st_rating,
                'creation_time': st_time,
                'author': st_author,
                'content': content,
                'tags': tags_lib
            }
            story_list.append(story_item)
            # Запись в файл в виде добавления чтобы не потерять результат при ошибке
            result_save(story_item, file_name)
            # Проверка на последний пост, переход на следующую страницу
            if st_id == last_story:
                break
            #
    print("[END] Parser time", time.time() - start_time)
    driver_pikabu.driver_end(driver)
    return (story_list)


def result_save(story_item, filename):
    with open(filename, mode='a+', encoding='utf-8') as file:
        json.dump(story_item, file, indent=2, ensure_ascii=False)
        file.write("\n")


def check_sponsor(story):
    try:
        story.find_element(By.CSS_SELECTOR, '.story__labels > .story__sponsor')
        return True
    except: return False


def get_content(story):
    content = dict()
    text_debug = 0
    image_debug = 0
    video_debug = 0
    st_text = ""
    st_img = []
    st_videos = []
    # Поиск текста в статье
    try:
        for part in story.find_elements(By.CSS_SELECTOR, '.story-block_type_text > p'):
            if part.text == "":
                continue
            st_text += part.text
    except:
        pass
    if st_text != "":
        content["text"] = st_text
        text_debug = 1
    # Поиск изображений в статье
    try:
        for img in story.find_elements(By.CSS_SELECTOR, '.story-image__image.image-loaded'):
            st_img.append(img.get_attribute('data-large-image'))
    except:
        pass
    if st_img != []:
        content["images"] = st_img
        image_debug = 1
    # Поиск видео в статье
    try:
        for video in story.find_elements(By.CSS_SELECTOR, '.story-block_type_video > .player'):
            _video = video.get_attribute('data-webm')
            if _video is None:
                _video = video.get_attribute('data-source')
            st_videos.append(_video)
    except:
        pass
    if st_videos != []:
        content["videos"] = st_videos
        video_debug = 1
    # Проверка на найденный контент
    if text_debug + image_debug + video_debug == 3:
        return False
    #
    return content


if __name__ == '__main__':
    print("[DEBUG] Parser_functions.py ")
