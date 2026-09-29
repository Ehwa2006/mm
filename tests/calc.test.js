const test = require('node:test');
const assert = require('node:assert');
const C = require('../src/assets/calc.js');

test('연봉 실수령액: 공제 항목 합과 실수령액이 맞는다', () => {
  const r = C.salary({ annual: 40000000, nonTaxMonthly: 200000, dependents: 1 });
  const sum = r.pension + r.health + r.longTermCare + r.employment + r.incomeTax + r.localTax;
  assert.strictEqual(r.totalDeductions, sum);
  assert.strictEqual(r.monthlyNet, Math.round(40000000 / 12 - sum));
  assert.strictEqual(r.pension, 148830); // (3,333,333 - 200,000) × 4.75%, 10원 미만 절사
  assert.strictEqual(r.localTax, Math.floor(r.incomeTax * 0.1 / 10) * 10);
});

test('국민연금은 기준소득월액 상한에서 멈춘다', () => {
  const r = C.salary({ annual: 200000000, nonTaxMonthly: 0 });
  assert.strictEqual(r.pension, Math.floor(6590000 * 0.0475 / 10) * 10);
});

test('부양가족·자녀가 많을수록 소득세가 줄어든다', () => {
  const a = C.salary({ annual: 60000000, dependents: 1 });
  const b = C.salary({ annual: 60000000, dependents: 4, children: 2 });
  assert.ok(b.incomeTax < a.incomeTax);
});

test('주휴수당: 주 40시간 최저시급이면 8시간분', () => {
  const r = C.weeklyHolidayPay({ hourly: 10320, weeklyHours: 40 });
  assert.strictEqual(r.weeklyHolidayPay, 82560);
});

test('주휴수당: 주 15시간 미만은 없음', () => {
  const r = C.weeklyHolidayPay({ hourly: 12000, weeklyHours: 14 });
  assert.strictEqual(r.eligible, false);
  assert.strictEqual(r.weeklyHolidayPay, 0);
});

test('주휴수당: 주 20시간이면 4시간분', () => {
  assert.strictEqual(C.weeklyHolidayPay({ hourly: 10000, weeklyHours: 20 }).weeklyHolidayPay, 40000);
});

test('퇴직금: 1년 근무, 3개월 900만원', () => {
  const r = C.severance({ startDate: '2025-01-01', lastDay: '2025-12-31', wages3m: 9000000 });
  assert.strictEqual(r.tenureDays, 365);
  assert.strictEqual(r.periodDays, 92); // 10/1 ~ 12/31
  assert.strictEqual(r.severancePay, Math.round(9000000 / 92 * 30));
});

test('퇴직금: 1년 미만은 0원', () => {
  const r = C.severance({ startDate: '2025-06-01', lastDay: '2026-05-30', wages3m: 9000000 });
  assert.strictEqual(r.eligible, false);
  assert.strictEqual(r.severancePay, 0);
});

test('변환기: 최저시급 → 월 2,156,880원', () => {
  const r = C.convertWage({ from: 'hourly', amount: 10320 });
  assert.strictEqual(r.monthly, 2156880);
  assert.strictEqual(r.belowMinimum, false);
  assert.strictEqual(C.convertWage({ from: 'monthly', amount: 2000000 }).belowMinimum, true);
});

test('연차: 1년 미만은 개월 수, 1년 15일, 3년 16일, 상한 25일', () => {
  assert.strictEqual(C.annualLeave({ startDate: '2026-01-01', baseDate: '2026-07-15' }).leaveDays, 6);
  assert.strictEqual(C.annualLeave({ startDate: '2025-01-01', baseDate: '2025-12-31' }).leaveDays, 11);
  assert.strictEqual(C.annualLeave({ startDate: '2025-01-01', baseDate: '2026-01-01' }).leaveDays, 15);
  assert.strictEqual(C.annualLeave({ startDate: '2023-01-01', baseDate: '2026-01-01' }).leaveDays, 16);
  assert.strictEqual(C.annualLeave({ startDate: '1990-01-01', baseDate: '2026-01-01' }).leaveDays, 25);
});

test('연차수당: 시급 × 8시간 × 미사용일수', () => {
  assert.strictEqual(C.annualLeave({ startDate: '2024-01-01', baseDate: '2026-01-01', hourly: 12000, unusedDays: 5 }).leavePay, 480000);
});

test('실업급여: 상한 68,100원, 하한 66,048원(8시간)', () => {
  const hi = C.unemployment({ wages3m: 15000000, periodDays: 92, insuredYears: 5 });
  assert.strictEqual(hi.dailyBenefit, 68100);
  assert.strictEqual(hi.cappedAt, 'max');
  assert.strictEqual(hi.benefitDays, 210);
  const lo = C.unemployment({ wages3m: 3000000, periodDays: 92, insuredYears: 0.5 });
  assert.strictEqual(lo.dailyBenefit, 66048);
  assert.strictEqual(lo.benefitDays, 120);
});

test('실업급여: 50세 이상은 소정급여일수가 길다', () => {
  assert.strictEqual(C.unemployment({ wages3m: 9000000, insuredYears: 10, over50: true }).benefitDays, 270);
});
