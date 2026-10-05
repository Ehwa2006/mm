const test = require('node:test');
const assert = require('node:assert');
const C = require('../src/assets/calc.js');

test('gaji pokok upah minimum 209 jam = ₩2.156.880', () => {
  assert.strictEqual(C.monthlyPay({ hourly: 10320 }).basePay, 2156880);
});

test('lembur 1,5x, malam +0,5x, libur ≤8 jam 1,5x, >8 jam 2x', () => {
  const r = C.monthlyPay({ hourly: 10000, overtimeHours: 10, nightHours: 10, holidayHours: 8, holidayOver8Hours: 2 });
  assert.strictEqual(r.overtimePay, 150000);
  assert.strictEqual(r.nightPay, 50000);
  assert.strictEqual(r.holidayPay, 120000 + 40000);
});

test('tempat kerja <5 pekerja: tanpa tambahan', () => {
  const r = C.monthlyPay({ hourly: 10000, overtimeHours: 10, nightHours: 10, holidayHours: 8, smallWorkplace: true });
  assert.strictEqual(r.overtimePay, 100000);
  assert.strictEqual(r.nightPay, 0);
  assert.strictEqual(r.holidayPay, 80000);
});

test('gaji bersih = kotor - potongan - asrama, konversi Rupiah', () => {
  const r = C.monthlyPay({ hourly: 10320, overtimeHours: 40, dormDeduction: 200000, exchangeRate: 11.5 });
  assert.strictEqual(r.net, r.gross - r.deductions.total - 200000);
  assert.strictEqual(r.netRupiah, Math.round(r.net * 11.5));
  assert.strictEqual(r.deductions.pension, Math.floor(r.gross * 0.0475 / 10) * 10);
});

test('upah di bawah minimum ditandai', () => {
  assert.strictEqual(C.monthlyPay({ hourly: 9000 }).belowMinimum, true);
  assert.strictEqual(C.monthlyPay({ hourly: 10320 }).belowMinimum, false);
});

test('pesangon 1 tahun, asuransi + selisih = pesangon', () => {
  const r = C.severance({ startDate: '2025-01-01', lastDay: '2025-12-31', wages3m: 9000000 });
  assert.strictEqual(r.tenureDays, 365);
  assert.strictEqual(r.severancePay, Math.round(9000000 / 92 * 30));
  assert.strictEqual(r.insuranceEstimate + r.employerDifference, r.severancePay);
});

test('pesangon kurang dari 1 tahun = 0', () => {
  const r = C.severance({ startDate: '2025-06-01', lastDay: '2026-05-30', wages3m: 9000000 });
  assert.strictEqual(r.eligible, false);
  assert.strictEqual(r.severancePay, 0);
});

test('pengembalian pensiun: 9% sebelum 2026, 9,5% di 2026', () => {
  const r = C.pensionRefund({ monthlyWage: 2000000, startMonth: '2025-11', endMonth: '2026-02', interestRate: 0 });
  assert.strictEqual(r.months, 4);
  assert.strictEqual(r.contributions, 180000 * 2 + 190000 * 2);
  assert.strictEqual(r.interest, 0);
});

test('pengembalian pensiun: bunga positif', () => {
  const r = C.pensionRefund({ monthlyWage: 2800000, startMonth: '2023-05', endMonth: '2026-04' });
  assert.strictEqual(r.months, 36);
  assert.ok(r.interest > 0 && r.total === r.contributions + r.interest);
});

test('uang libur mingguan: 40 jam upah minimum = 8 jam', () => {
  const r = C.weeklyHolidayPay({ hourly: 10320, weeklyHours: 40 });
  assert.strictEqual(r.weeklyHolidayPay, 82560);
  assert.strictEqual(C.weeklyHolidayPay({ hourly: 10000, weeklyHours: 20 }).weeklyHolidayPay, 40000);
  assert.strictEqual(C.weeklyHolidayPay({ hourly: 10000, weeklyHours: 14 }).eligible, false);
});

test('cuti tahunan: bulan pertama, 1 tahun 15 hari, 3 tahun 16 hari, maks 25', () => {
  assert.strictEqual(C.annualLeave({ startDate: '2026-01-01', baseDate: '2026-07-15' }).leaveDays, 6);
  assert.strictEqual(C.annualLeave({ startDate: '2025-01-01', baseDate: '2026-01-01' }).leaveDays, 15);
  assert.strictEqual(C.annualLeave({ startDate: '2023-01-01', baseDate: '2026-01-01' }).leaveDays, 16);
  assert.strictEqual(C.annualLeave({ startDate: '1990-01-01', baseDate: '2026-01-01' }).leaveDays, 25);
  assert.strictEqual(C.annualLeave({ startDate: '2024-01-01', baseDate: '2026-01-01', hourly: 12000, unusedDays: 5 }).leavePay, 480000);
});

test('tunjangan pengangguran: batas atas ₩68.100, batas bawah ₩66.048, hari', () => {
  const hi = C.unemployment({ wages3m: 15000000, periodDays: 92, insuredYears: 5 });
  assert.strictEqual(hi.dailyBenefit, 68100);
  assert.strictEqual(hi.benefitDays, 210);
  const lo = C.unemployment({ wages3m: 3000000, periodDays: 92, insuredYears: 0.5 });
  assert.strictEqual(lo.dailyBenefit, 66048);
  assert.strictEqual(lo.benefitDays, 120);
  assert.strictEqual(C.unemployment({ wages3m: 9000000, insuredYears: 10, over50: true }).benefitDays, 270);
});

test('gaji: tanpa asuransi pengangguran tidak ada potongan 고용보험', () => {
  assert.strictEqual(C.monthlyPay({ hourly: 10320, noEmploymentInsurance: true }).deductions.employment, 0);
  assert.ok(C.monthlyPay({ hourly: 10320 }).deductions.employment > 0);
});

test('batas potongan asrama: rumah 20%/15%, sementara 13%/8%, kelebihan', () => {
  const w = 2156880;
  assert.strictEqual(C.dormDeductionLimit({ ordinaryWage: w, housing: 'house', meals: true }).limit, Math.floor(w * 0.20));
  assert.strictEqual(C.dormDeductionLimit({ ordinaryWage: w, housing: 'house', meals: false }).limit, Math.floor(w * 0.15));
  assert.strictEqual(C.dormDeductionLimit({ ordinaryWage: w, housing: 'temporary', meals: true }).limit, Math.floor(w * 0.13));
  const r = C.dormDeductionLimit({ ordinaryWage: 2000000, housing: 'temporary', meals: false, actualDeduction: 250000 });
  assert.strictEqual(r.limit, 160000);
  assert.strictEqual(r.excess, 90000);
});

test('tabungan: sisa bulanan × bulan + pesangon + pensiun', () => {
  const r = C.savings({ monthlyNet: 2500000, monthlyLiving: 500000, months: 36, monthlyGross: 3000000, exchangeRate: 11.5 });
  assert.strictEqual(r.monthlySaving, 2000000);
  assert.strictEqual(r.saved, 72000000);
  assert.strictEqual(r.severance, 9000000);
  assert.strictEqual(r.pension, Math.round(3000000 * 0.095 * 36));
  assert.strictEqual(r.total, r.saved + r.severance + r.pension);
  assert.strictEqual(r.totalRupiah, Math.round(r.total * 11.5));
  assert.strictEqual(C.savings({ monthlyNet: 2500000, months: 11, monthlyGross: 3000000 }).severance, 0);
});

test('hari libur nasional: upah libur + 150%/200%, pekerja bulanan, <5 pekerja', () => {
  const r = C.publicHolidayPay({ hourly: 10000, hours: 10 });
  assert.strictEqual(r.paidHoliday, 80000);
  assert.strictEqual(r.workPay, 8 * 15000 + 2 * 20000);
  assert.strictEqual(r.total, 80000 + 160000);
  assert.strictEqual(C.publicHolidayPay({ hourly: 10000, hours: 8, monthlySalaried: true }).total, 120000);
  const s = C.publicHolidayPay({ hourly: 10000, hours: 8, smallWorkplace: true });
  assert.strictEqual(s.paidHoliday, 0);
  assert.strictEqual(s.workPay, 80000);
});
