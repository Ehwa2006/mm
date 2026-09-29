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
