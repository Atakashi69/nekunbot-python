prefix = '?'

class error_messages:
    unknown = ':x: Упс! Произошла какая-то ошибка. Обратитесь к администратору'
    timed_out = ':alarm_clock: Время вышло!'
    too_much_arguments = ':man_gesturing_no: Слишком много аргументов!'
    wrong_uid = ':red_circle: Неверный UID'
    invalid_cookie = ':card_box: В базе данных содержатся неверные куки или UID, авторизуйтесь заново или обратитесь к администратору'
    auth_fail = f':lock: Возможно, вы не авторизованы в системе, чтобы это сделать пропишите {prefix}auth'

class util_messages:
    auth1 = f'Здравствуйте, для авторизации вам надо отправить мне токен с сайта https://www.hoyolab.com\n' \
                                    f'**Инструкция только для ПК:**\n' \
                                    f'**1.** Авторизоваться на сайте\n' \
                                    f'**2.** Нажать правой кнопкой мыши в любом месте\n' \
                                    f'**3.** Кликнуть \'Просмотреть код элемента\' (см. 1 скрин)\n' \
                                    f'**4.** Зайти в раздел консоль и прописать там команду document.cookie, нажать Enter (см. 2 скрин)\n' \
                                    f'**5.** Ответ на эту команду выслать мне в ЛС\n' \
                                    f'https://imgur.com/ZdwhDUm\nhttps://imgur.com/udbN4cG\n\n' \
                                    f'**Инструкция для телефонов (работает и на ПК):**\n' \
                                    f'**1.** Авторизоваться на сайте\n' \
                                    f'**2.** Скопировать ссылку, отправленную мной следующим сообщением вставить её в поле вместо адреса, и, если требуется, дописать в начале ссылки \'javascript:\' (см. 3 скрин)\n' \
                                    f'**3.** В правом нижнем углу появится значок шестерёнки, нажмите на него и скопируйте токен (см. 4 скрин), а затем отправьте его мне в ЛС\n' \
                                    f'https://i.imgur.com/K7QXBhc.jpg\nhttps://i.imgur.com/HY87mlY.jpg'
    auth2 = '```javascript:(function(){var script=document.createElement("script");script.src="//cdn.takagg.com/eruda-v1/eruda.js";document.body.appendChild(script);script.onload=function(){eruda.init()}})();```'