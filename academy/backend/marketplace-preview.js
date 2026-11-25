"use strict";
function quotePreview(raw){
 if(typeof raw!=="string"||!/^(?:0|[1-9]\d{0,6})(?:[.,]\d{1,2})?$/.test(raw))return null;
 const [whole,frac=""]=raw.replace(",",".").split(".");
 const cents=BigInt(whole)*100n+BigInt(frac.padEnd(2,"0"));
 if(cents<1n||cents>100000000n)return null;
 const gross=cents*10000n,fee=gross/20n;
 return {gross,worker:gross-fee,fee};
}
function display(n){const frac=(n%1000000n).toString().padStart(6,"0").replace(/0+$/,"");return (n/1000000n).toString()+(frac?"."+frac:"")+" USDC"}
if(typeof module!=="undefined"&&module.exports)module.exports={quotePreview,display};
if(typeof document!=="undefined"){
const $=id=>document.getElementById(id);
const words={
en:["Payment preview","DEMONSTRATION ONLY — no real payments. Do not send funds.","Order amount (USDC)","Total","Freelancer (95%)","Academy (5%)","Payment unavailable","No wallet connection, payment link or transaction is generated.","Release readiness","Laboratory tests are not commercial approval.","Never repeat a payment if its status is uncertain. Contact support.","Enter 0.01–1,000,000 USDC with at most two decimal places.","Marketplace","Academy account",["Physical wallet compatibility","On-chain duplicate prevention and production contract identity","Independent security review","Commercial and legal review","Payment support and recovery"]],
ru:["Предпросмотр оплаты","ТОЛЬКО ДЕМОНСТРАЦИЯ — реальные платежи отключены. Не отправляйте средства.","Сумма заказа (USDC)","Всего","Исполнителю (95%)","Академии (5%)","Оплата недоступна","Кошелёк не подключается, платёжная ссылка и транзакция не создаются.","Готовность к запуску","Лабораторные тесты не означают коммерческое одобрение.","Не повторяйте оплату при неизвестном статусе. Обратитесь в поддержку.","Введите от 0,01 до 1 000 000 USDC, не более двух знаков после запятой.","Биржа заказов","Кабинет Академии",["Совместимость реальных кошельков","Защита от повторной оплаты и идентичность контракта","Независимая проверка безопасности","Коммерческая и юридическая проверка","Поддержка и восстановление платежей"]],
uk:["Перегляд оплати","ЛИШЕ ДЕМОНСТРАЦІЯ — реальні платежі вимкнено. Не надсилайте кошти.","Сума замовлення (USDC)","Разом","Виконавцю (95%)","Академії (5%)","Оплата недоступна","Гаманець не підключається, платіжне посилання й транзакція не створюються.","Готовність до запуску","Лабораторні тести не означають комерційного схвалення.","Не повторюйте платіж, якщо статус невідомий. Зверніться до підтримки.","Введіть від 0,01 до 1 000 000 USDC, не більше двох десяткових знаків.","Біржа замовлень","Кабінет Академії",["Сумісність реальних гаманців","Захист від повторної оплати та ідентичність контракту","Незалежна перевірка безпеки","Комерційна та юридична перевірка","Підтримка й відновлення платежів"]],
pl:["Podgląd płatności","TYLKO DEMONSTRACJA — prawdziwe płatności są wyłączone. Nie wysyłaj środków.","Kwota zlecenia (USDC)","Razem","Wykonawca (95%)","Akademia (5%)","Płatność niedostępna","Brak połączenia z portfelem, linku płatniczego i transakcji.","Gotowość do uruchomienia","Testy laboratoryjne nie oznaczają zgody na start komercyjny.","Nie ponawiaj płatności przy nieznanym statusie. Skontaktuj się ze wsparciem.","Wpisz 0,01–1 000 000 USDC, maksymalnie dwa miejsca po przecinku.","Giełda zleceń","Panel Akademii",["Zgodność z rzeczywistymi portfelami","Ochrona przed powtórną płatnością i tożsamość kontraktu","Niezależna kontrola bezpieczeństwa","Przegląd komercyjny i prawny","Wsparcie i odzyskiwanie płatności"]]};
const ids=["heading","warning","amountLabel","grossLabel","workerLabel","feeLabel","pay","note","statusHeading","status","support","error","back","account"];
const lang=new URLSearchParams(location.search).get("lang");
$("lang").value=Object.hasOwn(words,lang)?lang:"en";
function update(){const p=quotePreview($("amount").value);$("result").hidden=!p;$("error").hidden=!!p;if(p){$("total").textContent=display(p.gross);$("worker").textContent=display(p.worker);$("fee").textContent=display(p.fee)}}
function translate(){const l=$("lang").value,w=words[l];document.documentElement.lang=l;ids.forEach((id,i)=>$(id).textContent=w[i]);$("blockers").replaceChildren(...w[14].map(t=>{const li=document.createElement("li");li.textContent=t;return li}));$("back").href="/marketplace?lang="+l;$("account").href="/dashboard?lang="+l;update()}
$("amount").addEventListener("input",update);$("lang").addEventListener("change",translate);translate();
}
