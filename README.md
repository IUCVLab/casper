# CASPER
Collection &amp; Analysis of Scientific Preprints for Education &amp; Research (CASPER)

Данный сервис позволяет скачивать препринты статей по их названиям. Он также распознаёт и очищает текст статей, раскрывает аббревиатуры.

Чтобы установить сервис на свой компьютер склонируйте данный репозиторий:
```
git clone https://github.com/IUCVLab/casper.git
```

Затем установите зависимости:

```
python3 -m pip install -r requirements.txt
```

После этого достаточно запустить скрипт сервера, и на вашей машине запустится приложение по адресу `http://localhost:1234/`.
```
./start.sh
```

Следуйте инструкциям на экране. Если что-то не работает - заводите баг на гитхабе )