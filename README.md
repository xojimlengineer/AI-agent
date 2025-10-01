📊 Data Analytics AI Agent

Bu loyiha foydalanuvchi bergan oddiy tabiy til savollarini qabul qilib, ularni avtomatik tarzda SQL so‘rovlariga aylantiradi va natijani Excel fayl ko‘rinishida qaytaradi. Excel faylida jadval bilan bir qatorda ustunli diagramma (bar chart) va chiziqli diagramma (line chart) ham yaratiladi. Foydalanuvchi tayyor faylni yuklab olib, uni o‘z tahlil jarayonida ishlatishi mumkin.

🗄️ Ma’lumotlar bazasi modeli

Dasturda foydalanilgan SQLite bazasi uchta asosiy jadvaldan iborat:

Clients (Mijozlar)
Ustun nomi	Izoh
id	Mijozning noyob identifikatori
name	Mijozning to‘liq ismi
birth_date	Tug‘ilgan sanasi
region	Mijoz yashaydigan hudud
Accounts (Hisoblar)
Ustun nomi	Izoh
id	Hisob raqami identifikatori
client_id	Clients.id bilan bog‘langan tashqi kalit
balance	Hisobdagi mavjud mablag‘
open_date	Hisob ochilgan sana
Transactions (Tranzaksiyalar)
Ustun nomi	Izoh
id	Tranzaksiya identifikatori
account_id	Accounts.id bilan bog‘langan tashqi kalit
amount	Tranzaksiya summasi
date	Tranzaksiya sanasi
type	Tranzaksiya turi (masalan, kirim yoki chiqim)
🚀 Qanday ishlaydi?

Foydalanuvchi savol kiritadi:
“Toshkent bo‘yicha 2022 va 2023-yillardagi umumiy tranzaksiyalar summasini taqqoslab ber”

AI Agent bu savolni SQL query ga aylantiradi:

SELECT strftime('%Y', t.date) AS year, SUM(t.amount) AS total_transactions
FROM Transactions t
JOIN Accounts a ON t.account_id = a.id
JOIN Clients c ON a.client_id = c.id
WHERE c.region = 'Tashkent' AND (strftime('%Y', t.date) = '2022' OR strftime('%Y', t.date) = '2023')
GROUP BY year
ORDER BY year;


Olingan natija Excel faylga yoziladi (jadval + grafik avtomatik chiziladi).

Foydalanuvchi Streamlit dasturi orqali natija faylini yuklab oladi.