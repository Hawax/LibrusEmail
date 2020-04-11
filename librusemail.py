from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import sys
import os
import sys
import msvcrt
import getpass_ak
from cryptography.fernet import Fernet

def save_creds_and_read():
    """Zapisuje po prostu haslo i login jesli juz to wczesniej zrobil odczytuje je
    :return 2 strings
    """
    haslo_do_szyfrowania = "MqD3GL8lYxBSCEz07Is9997maipFOHDtwQSYtLryOFU="    
    f = Fernet(haslo_do_szyfrowania)
    try:
        with open("login_i_hasło.txt", 'r') as file:
            login, haslo = file.readlines()
            haslo = f.decrypt(haslo.encode('utf-8'))
            return login, haslo.decode('utf-8')
    except FileNotFoundError:
        login = input('Login librus: ')
        haslo = (getpass_ak.getpass('Hasło librus: '))
        haslo = haslo.encode()
        haslo = f.encrypt(haslo)

        with open("login_i_hasło.txt", 'a+') as file:
            file.write(login + '\n')
            file.write(haslo.decode('utf-8'))
        return login, haslo


def create_web_driver(headless):
    """Tworzy webdrivera
     :return webdriver
     """
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    prefs = {
        'download.default_directory':
            os.path.abspath(os.getcwd() + r'\Zdjecia'),
        "profile.default_content_setting_values.automatic_downloads": 1
    }
    chrome_options.add_experimental_option('prefs', prefs)
    web_inside = webdriver.Chrome('chromedriver.exe',
                                  chrome_options=chrome_options)
    web_inside.set_window_size(1366, 968)
    web_inside.get('https://portal.librus.pl/rodzina/synergia/loguj')

    return web_inside


def make_folder_for_attachments():
    execution_path = os.getcwd()

    if not os.path.exists(execution_path):
        os.mkdir('Zdjecia')
        print("Directory ", 'Zdjecia', " Created ")
    else:
        pass


def clean_dirname(dirname):
    for symbol in ["/", "\\", ":", ":", "*", "<", ">", "|", '"', ","]:
        dirname = dirname.replace(symbol, '')

    return dirname


def get_download_links(web_driver, dirname):
    """Stara się pobierać załączniki, sortować je, oczywiście librus musi wszystko kompikować i są pobierane w osobnym
    oknie z unikalnym id itp.
    """

    # lista załączników
    parentElement = web_driver.find_element_by_xpath(
        "/html/body/div[3]/div[3]/form/div/div/table/tbody/tr/td[2]/table[3]/tbody"
    )
    elementList = parentElement.find_elements_by_tag_name("tr")
    i = 2  # zaczynamy od dwójki bo pierwszy element ma id tr[2] no wiadomo ocb

    # nieeleganco ale leci po kolei i sprawdza czy jest załącznik jeśli nie ma to znaczy ze nie ma więcej
    for list in elementList:
        print(list.text)
        try:
            click_link = web_driver.find_element_by_xpath(
                '/html/body/div[3]/div[3]/form/div/div/table/tbody/tr/td[2]/table[3]/tbody/tr[{}]/td[2]/a/img'
                    .format(i))
            click_link.click()
            i += 1
            time.sleep(15)  # czeka aż plik się pobierze
        except:
            break

    # teraz tworzy folder z tematem zajęć w folderze Zdjecia
    try:
        if i >= 3:
            dirname = clean_dirname(dirname)  # czyści niedozwolone znaki
            main_folder = 'Zdjecia'
            dirname = main_folder + '\\' + dirname[0:40]  # maksymana długość nazwy folderu, bo inaczej coś się bugowało

            onlyfiles = [
                f for f in os.listdir(main_folder)
                if os.path.isfile(os.path.join(main_folder, f))
            ]  # tutaj poszukuje plików i kopjuje je do folderu, który zostanie zaraz stworzony
            print(onlyfiles)
            make_folder_for_attachments()

            if not os.path.exists(dirname):
                os.mkdir(dirname)
                print("Directory ", dirname, " Created ")
            else:
                print("Directory ", dirname, " already exists")

            for file in onlyfiles:  # sortuje je do folderu
                print(file)
                os.rename(main_folder + '\\' + file, dirname + '\\' + file)

    except Exception as e:
        print(e)


def password_and_username_fill(web_driver, login_inside, haslo_inside):
    try:
        input_click_cookies = web_driver.find_element_by_xpath(
            '/html/body/main/article/div[1]/div[1]/div[7]/div/a')
        input_click_cookies.click()
    except:
        pass
    time.sleep(5)
    input_click1 = web_driver.find_element_by_xpath(
        '/html/body/nav/div/div[1]/div/div[2]/a[3]')
    input_click1.click()
    time.sleep(1)

    input_click2 = web_driver.find_element_by_xpath(
        '/html/body/nav/div/div[1]/div/div[2]/div/a[2]')
    input_click2.click()
    time.sleep(10)

    input_element = web_driver  # musi zmienic ramke, bo logowanie jest wsadzone w iframe.
    input_element.switch_to_frame('caLoginIframe')

    login_click = input_element.find_element_by_xpath(
        '/html/body/div[4]/div/div/div[1]/div[3]/div[1]/div[1]/input')
    login_click.send_keys(login_inside)
    time.sleep(1)

    haslo_click = input_element.find_element_by_xpath(
        '/html/body/div[4]/div/div/div[1]/div[3]/div[2]/div[1]/input')
    haslo_click.send_keys(haslo_inside)
    time.sleep(1)

    input_element_login_click = web_driver.find_element_by_xpath(
        "/html/body/div[4]/div/div/div[2]/button")
    input_element_login_click.click()


def click_on_email_icon(web_driver):
    time.sleep(10)
    wiadomosci = web_driver.find_element_by_xpath(
        '/html/body/div[3]/div[1]/div[2]/div/ul/li[3]/a[1]/span')
    wiadomosci.click()


def get_messages(web_driver):
    linki_url = []
    linki_url_text = []
    for i in range(1, 55):
        try:  # nie robię tego .format gdyż tak wygląda według mnie czytelniej
            href_url = web_driver.find_element_by_xpath(
                "/html/body/div[3]/div[3]/form/div/div/table/tbody/tr/td[2]/table[2]/tbody/tr["
                + str(i) + "]/td[4]/a").get_attribute('href')

            href_url_text = web_driver.find_element_by_xpath(
                "/html/body/div[3]/div[3]/form/div/div/table/tbody/tr/td[2]/table[2]/tbody/tr["
                + str(i) + "]/td[4]/a").text

            href_bold = web_driver.find_element_by_xpath(
                "/html/body/div[3]/div[3]/form/div/div/table/tbody/tr/td[2]/table[2]/tbody/tr["
                + str(i) + "]/td[4]").get_attribute('style')

            if 'bold' in str(href_bold):  # tutaj sprawdza czy temat został odczytany czy nie i dodaje je do listy.
                print(href_url)
                print(href_url_text, '\n')
                with open("przeczytane_tematy.txt", 'a+') as file:
                    temat = href_url_text + ' ----- URL: ' + href_url + '\n' + '\n'
                    file.write(temat)

                linki_url.append(href_url)
                linki_url_text.append(href_url_text)
        except:
            pass

    all = zip(linki_url, linki_url_text
              )  # tutaj odczytuje poczte i zapisuje załączniki(niestety
    for url_do_poczty, zalaczniki in all:  # zapisywanie załączników działa niestety tylko w trybie bez headless)
        web_driver.get(url_do_poczty)
        time.sleep(5)  # czeka aż się strona naładuje
        get_download_links(web_driver, zalaczniki)
        time.sleep(3)


def read_messages(web_driver):
    get_messages(web_driver)
    print('--BRAK NOWYCH WIADOMOŚCI--')


def countdown(steps):
    for remaining in range(steps, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} sekund pozostało.".format(remaining))
        sys.stdout.flush()
        time.sleep(1)

    sys.stdout.write("\rOd nowa!            \n")


def howmuch():
    """Pyta się użytkownika co ile ma sprawdzać pocztę
    :return int
    """
    try:
        how_many = input(
            "Co ile minut ma minut ma sprawdzać pocztę Librusa? (min - 20 minut): "
        )
        if int(how_many) >= 20:
            return how_many
        else:
            print('Za mało minut')
            return howmuch()
    except:
        print("Musi to być liczba całkowita")
        return howmuch()


def get_answer_headless():
    """Pyta się o to czy ma działać w tle czy nie tzw.headless
        :return string
    """
    how_many = input("Chcesz żeby bot działał w tle?: ")
    if how_many.lower() == 'tak':
        return 1
    elif how_many.lower() == 'nie':
        return 0
    else:
        print('Musi byc tak lub nie')
        return get_answer_headless()


def main(check):
    login, haslo = save_creds_and_read()
    web_driver = create_web_driver(
        check)  # tworzę nowy webdriver gdyż nie chce żeby stał bezczynnie w tle.

    try:
        password_and_username_fill(web_driver, login, haslo)
        click_on_email_icon(web_driver)
        read_messages(web_driver)
        web_driver.close()

    except:
        web_driver.close()
        print(
            'Najprawdopodbniej coś poszło nie tak i strona się nie załadowała lub przekroczyłeś limit '
            'zapytań do strony więc czekamy chwilkę i próbujemy od nowa')
        time.sleep(30)
        return main(check)


ile_min = howmuch()
tak_nie = get_answer_headless()

i = 0
while True:
    main(tak_nie)
    i += 1
    print('Tyle razy już sprawdziłem pocztę :) - ', i)
    countdown(int(ile_min) * 60)
