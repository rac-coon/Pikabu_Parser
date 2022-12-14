import datetime
import tkinter
from tkcalendar import Calendar
import parser_functions as parser


def start():
    first_date = cal_first.get_date()
    first = datetime.datetime.strptime(first_date, '%d.%m.%Y')
    second_date = cal_second.get_date()
    second = datetime.datetime.strptime(second_date, '%d.%m.%Y')
    if first <= second:
        if section_check():
            test_label["text"] = "Программа работает"
            first_date = str(first_date).replace(".", "-")
            second_date = str(second_date).replace(".", "-")
            url = f"https://pikabu.ru/best/{first_date}_{second_date}"
            if radio.get() == "community":
                url = input_url.get()
            parser.url_pars(url)
    else:
        test_label["text"] = "Начальная дата не может быть больше конечной"


def section_check():
    if radio.get() == "None":
        test_label["text"] = "Не выбран тип поиска"
        return False
    elif radio.get() == "community":
        url = input_url.get()
        try:
            url = url.split("/community/")
            url = url[1]
        except IndexError:
            test_label["text"] = "Неверный формат ссылки"
            return False
    return True


def community_url():
    url = input_url.get()
    if url == "":
        return
    try:
        url = url.split("/community/")
        url = url[1]
    except IndexError:
        test_label["text"] = "Неверный формат ссылки"

if __name__ == "__main__":
    # Create Object
    #window = Tk()
    window = tkinter.Tk()
    # Set geometry
    window.geometry("800x500")

    starting_date = datetime.date(year=2010, month=9, day=1)
    last_date = datetime.date.today()

    # Add Calendar
    cal_first = Calendar(window, selectmode='day', year=2022,
                         month=6, day=1, mindate=starting_date,
                         maxdate=last_date, locale="ru_RU")
    cal_first.place(x=100, y=50)
    tkinter.Label(text="Начальная дата:", font=('Aerial 11')).place(x=150, y=20)

    # Add Second Calendar
    cal_second = Calendar(window, selectmode='day', year=2022,
                          month=6, day=1, mindate=starting_date,
                          maxdate=last_date, locale="ru_RU")
    cal_second.place(x=450, y=50)
    tkinter.Label(text="Конечная дата:", font=('Aerial 11')).place(x=500, y=20)

    # Define radiobutton
    radio = tkinter.StringVar()
    radio.set("None")
    tkinter.Radiobutton(window, text="Лучшие", variable=radio, value="best").place(x=100, y=260)
    tkinter.Radiobutton(window, text="Свежее", variable=radio, value="new").place(x=200, y=260)
    tkinter.Radiobutton(window, text="Сообщество", variable=radio, value="community").place(x=300, y=260)



    # Add Button and Label and Entry
    tkinter.Button(window, text="Начать", command=start).place(x=590, y=260)
    test_label = tkinter.Label(text="")
    test_label.place(x=300, y=330)
    input_url = tkinter.Entry(window)
    input_url.place(x=330, y=290)
    tkinter.Label(text="URL").place(x=300, y=290)
    #input_url.insert(0, "url сообщества")

    # Execute Tkinter
    window.mainloop()
