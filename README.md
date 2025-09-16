# City Alerts API

Сервіс для пошуку територіальних одиниць з державних реєстрів. Інтеграція з повітряними тривогами, щоб повертати адміністративний код локації із загрозою

<a href="https://send.monobank.ua/jar/6dpG1MjjQb" target="_blank"><img src="https://github.com/riadinskyi/city-alert-registry/blob/master/support-with-monobank-git.png?raw=true" alt="Support with Monobank" height="41" width="180"></a>

> [!CAUTION]
> Доступ до API та використання його вмісту здійснюються **виключно на власний ризик**.  
> **Розробник за жодних обставин не несе відповідальності** перед будь-якою стороною за будь-які прямі, непрямі, випадкові, особливі чи інші збитки, що можуть виникнути внаслідок використання наданої інформації.
>
> Також ми не гарантуємо безперервну роботу сервісу та не несемо відповідальності за його тимчасову недоступність через технічні причини.
>
> Використовуючи API, Ви автоматично погоджуєтесь брати на себе всю відповідальність, що може виникнути під час його застосування.

## ℹ️ Джерела інформації
|                                                                                                                          Назва                                                                                                                           |                                                          Ресурси                                                          |                                                Ліцензія                                                |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------------------------------------------------:|:------------------------------------------------------------------------------------------------------:|
| [Кодифікатор адміністративно-територіальних <br/>одиниць та територій територіальних громад](https://mindev.gov.ua/diialnist/rozvytok-mistsevoho-samovriaduvannia/kodyfikator-administratyvno-terytorialnykh-odynyts-ta-terytorii-terytorialnykh-hromad) |                        [Міністрество розвитку громад та територій України](https://mindev.gov.ua)                         | [Creative Commons Attribution 4.0 International license](https://creativecommons.org/licenses/by/4.0/) |
|                                                                                        [Alerts.in.ua](https://devs.alerts.in.ua/#documentationgeneral_disclaimer)                                                                                        | - [Посилання на бібліотеку](https://pypi.org/project/alerts-in-ua/)    <br/>  - [Документація](https://devs.alerts.in.ua) |                               [MIT](https://opensource.org/license/mit)                                |
|                                                                                                                [Офіційні повітряні тривоги](https://www.ukrainealarm.com)                                                                                                                |                           [Отримати API ключ](https://api.ukrainealarm.com)<br/> - [Документація](https://api.ukrainealarm.com/swagger/index.html)                           |                                             _Дані відсутні_                                              |


## ⚠️ Requirements
- Python 3.9+
- Poetry
- API токен від провайдерів даних 
- (Офіційні Повітряні Тривоги або Alerts.in.ua)


## 📈 Функціонал
- Пошук територіальних одиниць України (області, райони, громади, міста, села та селища)
- Ієрхаїчний пошук за областю - районом - територіальної громадою - міста, села, селища
- Отримання інформації про нагальні повітряні тривоги

## 🪛 Prerequisites
1. Отримати API ключ
> [!TIP]
> Провайдеру краще написати своїми словами для чого буде використовуватися їхні послуги, а не текс згенерований LLM (Gemini, DeepSeek, ChatGPT etc.)
- **Офіційні повітряні тривоги**:
  - Перейти на сторінку [Для розробників (АПІ)](https://www.ukrainealarm.com)→ заповнити форму та отримати ключ на електрону пошту
- **Alerts In UA:**
  - Заповнити [форму](https://alerts.in.ua/api-request) та отримати ключ на пошту

2. Install Python packaging and dependency manager:
`pip install poetry
`
## ⚙️ Setup
1. Install dependencies 
   ```bash
   poetry install
   ```
2. Set environment variables
Create ´.env´ file and set next variables:
* **CORRECT_TOKEN** - Ваш власний токен, щоб надавати доступ до функціоналу
* **AIR_ALERT_API_TOKEN_IN_UA** - токен від провайдеру даних [air-alert.in.ua](https://air-alert.in.ua)
* **AIR_ALERT_API_TOKEN_OFFICIAL** - токен від [Офіційні повітряні тривоги](https://api.ukrainealarm.com)
3. Запустити програму `uvicorn main:app --host 0.0.0.0 --port 10000`


