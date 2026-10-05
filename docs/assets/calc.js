/* Perhitungan gaji pekerja di Korea (standar 2026). Dipakai di browser (window.Calc) dan Node (require). */
(function (root) {
  var RATES = {
    year: 2026,
    minimumWage: 10320,          // upah minimum per jam 2026
    monthlyHours: 209,           // jam dasar per bulan (40 jam/minggu + 주휴)
    pension: 0.0475,             // 국민연금 bagian pekerja (total 9,5%)
    pensionMin: 410000,          // batas bawah dasar iuran (Jul 2026 - Jun 2027)
    pensionMax: 6590000,         // batas atas dasar iuran
    health: 0.03595,             // 건강보험 bagian pekerja
    longTermCare: 0.9448 / 7.19, // 장기요양 = iuran kesehatan × 13,14%
    employment: 0.009,           // 고용보험 bagian pekerja (bagian tunjangan pengangguran)
    jobSeekMax: 68100            // batas atas tunjangan pengangguran per hari (2026)
  };

  function floor10(n) { return Math.floor(n / 10) * 10; }

  function earnedIncomeDeduction(gross) {
    var d;
    if (gross <= 5000000) d = gross * 0.7;
    else if (gross <= 15000000) d = 3500000 + (gross - 5000000) * 0.4;
    else if (gross <= 45000000) d = 7500000 + (gross - 15000000) * 0.15;
    else if (gross <= 100000000) d = 12000000 + (gross - 45000000) * 0.05;
    else d = 14750000 + (gross - 100000000) * 0.02;
    return Math.min(d, 20000000);
  }

  var BRACKETS = [
    [14000000, 0.06, 0], [50000000, 0.15, 1260000], [88000000, 0.24, 5760000],
    [150000000, 0.35, 15440000], [300000000, 0.38, 19940000],
    [500000000, 0.40, 25940000], [1000000000, 0.42, 35940000], [Infinity, 0.45, 65940000]
  ];

  function progressiveTax(base) {
    if (base <= 0) return 0;
    for (var i = 0; i < BRACKETS.length; i++) {
      if (base <= BRACKETS[i][0]) return base * BRACKETS[i][1] - BRACKETS[i][2];
    }
  }

  function earnedIncomeTaxCredit(tax, gross) {
    var credit = tax <= 1300000 ? tax * 0.55 : 715000 + (tax - 1300000) * 0.3;
    var limit;
    if (gross <= 33000000) limit = 740000;
    else if (gross <= 70000000) limit = Math.max(660000, 740000 - (gross - 33000000) * 0.008);
    else if (gross <= 120000000) limit = Math.max(500000, 660000 - (gross - 70000000) * 0.5);
    else limit = Math.max(200000, 500000 - (gross - 120000000) * 0.5);
    return Math.min(credit, limit);
  }

  /* Potongan bulanan dari gaji kotor bulanan (lajang, tanpa tanggungan). */
  function deductions(monthlyGross, noEmploymentInsurance) {
    var m = Math.max(0, monthlyGross);
    var pensionBase = Math.min(Math.max(m, RATES.pensionMin), RATES.pensionMax);
    var pension = m > 0 ? floor10(pensionBase * RATES.pension) : 0;
    var health = floor10(m * RATES.health);
    var care = floor10(health * RATES.longTermCare);
    var employment = noEmploymentInsurance ? 0 : floor10(m * RATES.employment);
    var annual = m * 12;
    var taxBase = annual - earnedIncomeDeduction(annual) - 1500000 - (pension + health + care + employment) * 12;
    var computed = progressiveTax(Math.max(0, taxBase));
    var annualTax = Math.max(0, computed - earnedIncomeTaxCredit(computed, annual) - 130000);
    var incomeTax = floor10(annualTax / 12);
    var localTax = floor10(incomeTax * 0.1);
    return {
      pension: pension, health: health, longTermCare: care, employment: employment,
      incomeTax: incomeTax, localTax: localTax,
      total: pension + health + care + employment + incomeTax + localTax
    };
  }

  /* Gaji bulanan: gaji pokok + lembur (연장), malam (야간), hari libur (휴일).
     Tambahan 50% untuk lembur/malam/libur ≤8 jam, 100% untuk libur >8 jam (usaha ≥5 pekerja). */
  function monthlyPay(opts) {
    var hourly = Math.max(0, +opts.hourly || 0);
    var baseHours = Math.max(0, opts.baseHours == null ? RATES.monthlyHours : +opts.baseHours);
    var overtime = Math.max(0, +opts.overtimeHours || 0);
    var night = Math.max(0, +opts.nightHours || 0);
    var holiday = Math.max(0, +opts.holidayHours || 0);
    var holidayOver8 = Math.max(0, +opts.holidayOver8Hours || 0);
    var small = !!opts.smallWorkplace; // usaha <5 pekerja: tanpa tambahan 50%

    var basePay = Math.round(hourly * baseHours);
    var premium = small ? 1 : 1.5;
    var overtimePay = Math.round(hourly * overtime * premium);
    var nightPay = small ? 0 : Math.round(hourly * night * 0.5);
    var holidayPay = Math.round(hourly * (holiday * premium + holidayOver8 * (small ? 1 : 2)));
    var gross = basePay + overtimePay + nightPay + holidayPay;

    var d = deductions(gross, opts.noEmploymentInsurance);
    var dorm = Math.max(0, +opts.dormDeduction || 0);
    var net = gross - d.total - dorm;
    var rate = Math.max(0, +opts.exchangeRate || 0);
    return {
      basePay: basePay, overtimePay: overtimePay, nightPay: nightPay, holidayPay: holidayPay,
      gross: gross, deductions: d, dormDeduction: dorm, net: net,
      netRupiah: rate ? Math.round(net * rate) : null,
      belowMinimum: hourly > 0 && hourly < RATES.minimumWage
    };
  }

  function parseDate(s) {
    var p = String(s).split('-').map(Number);
    return new Date(Date.UTC(p[0], p[1] - 1, p[2]));
  }
  function daysBetween(a, b) { return Math.round((b - a) / 86400000); }

  /* Pesangon (퇴직금): upah rata-rata harian × 30 × (hari kerja / 365). lastDay = hari kerja terakhir. */
  function severance(opts) {
    var start = parseDate(opts.startDate);
    var retire = parseDate(opts.lastDay);
    retire.setUTCDate(retire.getUTCDate() + 1);
    var tenureDays = daysBetween(start, retire);
    var from = new Date(retire);
    from.setUTCMonth(from.getUTCMonth() - 3);
    var periodDays = daysBetween(from, retire);
    var wages3m = Math.max(0, +opts.wages3m || 0) + Math.max(0, +opts.annualBonus || 0) * 3 / 12;
    var avgDaily = periodDays > 0 ? wages3m / periodDays : 0;
    var eligible = tenureDays >= 365;
    var pay = eligible ? Math.round(avgDaily * 30 * tenureDays / 365) : 0;
    // Asuransi kepulangan (출국만기보험): majikan menyetor 8,3% upah bulanan; selisihnya dibayar majikan.
    var monthlyWage = Math.max(0, +opts.wages3m || 0) / 3;
    var insuranceEstimate = eligible ? Math.round(monthlyWage * 0.083 * tenureDays / 365 * 12) : 0;
    return {
      eligible: eligible,
      tenureDays: tenureDays,
      periodDays: periodDays,
      averageDailyWage: Math.round(avgDaily),
      severancePay: pay,
      insuranceEstimate: Math.min(insuranceEstimate, pay),
      employerDifference: Math.max(0, pay - insuranceEstimate)
    };
  }

  /* Pengembalian pensiun (반환일시금): iuran pekerja + majikan + bunga sederhana (perkiraan). */
  function pensionRefund(opts) {
    var wage = Math.max(0, +opts.monthlyWage || 0);
    var start = parseDate(opts.startMonth + '-01');
    var end = parseDate(opts.endMonth + '-01');
    var interest = opts.interestRate == null ? 0.03 : +opts.interestRate;
    var base = Math.min(Math.max(wage, RATES.pensionMin), RATES.pensionMax);
    var months = 0, contributions = 0, interestTotal = 0;
    for (var d = new Date(start); d <= end; d.setUTCMonth(d.getUTCMonth() + 1)) {
      var y = d.getUTCFullYear();
      var rate = y >= 2026 ? 0.09 + 0.005 * Math.min(y - 2025, 8) : 0.09; // naik 0,5%p per tahun sejak 2026
      var c = floor10(base * rate);
      var monthsToEnd = (end.getUTCFullYear() - y) * 12 + end.getUTCMonth() - d.getUTCMonth();
      contributions += c;
      interestTotal += c * interest * monthsToEnd / 12;
      months++;
    }
    return {
      months: months,
      contributions: contributions,
      interest: Math.round(interestTotal),
      total: Math.round(contributions + interestTotal)
    };
  }

  /* Uang libur mingguan (주휴수당): kerja ≥15 jam/minggu → (jam/40 × 8 jam) × upah per jam */
  function weeklyHolidayPay(opts) {
    var hourly = Math.max(0, +opts.hourly || 0);
    var hours = Math.max(0, +opts.weeklyHours || 0);
    var eligible = hours >= 15;
    var holidayHours = eligible ? Math.min(hours, 40) / 40 * 8 : 0;
    var weeklyPay = Math.round(holidayHours * hourly);
    return {
      eligible: eligible,
      holidayHours: Math.round(holidayHours * 100) / 100,
      weeklyHolidayPay: weeklyPay,
      monthlyHolidayPay: Math.round(weeklyPay * 365 / 7 / 12),
      belowMinimum: hourly > 0 && hourly < RATES.minimumWage
    };
  }

  /* Cuti tahunan (연차): <1 tahun 1 hari per bulan (maks 11), lalu 15 hari + 1 per 2 tahun (maks 25) */
  function annualLeave(opts) {
    var start = parseDate(opts.startDate);
    var on = parseDate(opts.baseDate);
    var months = (on.getUTCFullYear() - start.getUTCFullYear()) * 12 + on.getUTCMonth() - start.getUTCMonth();
    if (on.getUTCDate() < start.getUTCDate()) months--;
    months = Math.max(0, months);
    var years = Math.floor(months / 12);
    var days = years < 1 ? Math.min(months, 11) : Math.min(15 + Math.floor((years - 1) / 2), 25);
    var hourly = Math.max(0, +opts.hourly || 0);
    var unused = Math.max(0, +opts.unusedDays || 0);
    return {
      yearsWorked: years,
      monthsWorked: months,
      leaveDays: days,
      leavePay: Math.round(hourly * 8 * unused)
    };
  }

  var JOB_SEEK_DAYS = [ // [masa asuransi minimal (tahun), <50 tahun, ≥50 tahun/disabilitas]
    [10, 240, 270], [5, 210, 240], [3, 180, 210], [1, 150, 180], [0, 120, 120]
  ];

  /* Tunjangan pengangguran (구직급여): 60% upah rata-rata harian, batas atas ₩68.100, batas bawah 80% upah minimum */
  function unemployment(opts) {
    var wages3m = Math.max(0, +opts.wages3m || 0);
    var periodDays = Math.max(1, +opts.periodDays || 92);
    var dailyHours = Math.min(8, Math.max(1, +opts.dailyHours || 8));
    var insuredYears = Math.max(0, +opts.insuredYears || 0);
    var avgDaily = wages3m / periodDays;
    var min = RATES.minimumWage * 0.8 * dailyHours;
    var raw = avgDaily * 0.6;
    var daily = Math.round(Math.max(min, Math.min(raw, RATES.jobSeekMax)));
    var row = JOB_SEEK_DAYS.filter(function (r) { return insuredYears >= r[0]; })[0];
    var days = opts.over50 ? row[2] : row[1];
    return {
      averageDailyWage: Math.round(avgDaily),
      dailyBenefit: daily,
      cappedAt: raw > RATES.jobSeekMax ? 'max' : raw < min ? 'min' : null,
      benefitDays: days,
      monthlyBenefit: daily * 30,
      totalBenefit: daily * days
    };
  }

  /* Batas potongan asrama/makan (숙식비 공제지침): % dari upah normal bulanan (통상임금) */
  var DORM_LIMITS = { house: { meals: 0.20, none: 0.15 }, temporary: { meals: 0.13, none: 0.08 } };

  function dormDeductionLimit(opts) {
    var wage = Math.max(0, +opts.ordinaryWage || 0);
    var rate = DORM_LIMITS[opts.housing === 'temporary' ? 'temporary' : 'house'][opts.meals ? 'meals' : 'none'];
    var limit = Math.floor(wage * rate);
    var actual = Math.max(0, +opts.actualDeduction || 0);
    return { rate: rate, limit: limit, excess: Math.max(0, actual - limit) };
  }

  /* Tabungan: (gaji bersih - biaya hidup - kiriman bulanan dipakai keluarga) × bulan + pesangon & pensiun perkiraan */
  function savings(opts) {
    var net = Math.max(0, +opts.monthlyNet || 0);
    var living = Math.max(0, +opts.monthlyLiving || 0);
    var months = Math.max(0, Math.floor(+opts.months || 0));
    var gross = Math.max(0, +opts.monthlyGross || 0);
    var monthly = Math.max(0, net - living);
    var saved = monthly * months;
    // Pesangon ≈ 1 bulan gaji per tahun (hanya jika ≥ 12 bulan); pensiun ≈ 9,5% gaji per bulan
    var severance = months >= 12 ? Math.round(gross * months / 12) : 0;
    var pension = Math.round(gross * 0.095 * months);
    var total = saved + severance + pension;
    var rate = Math.max(0, +opts.exchangeRate || 0);
    return {
      monthlySaving: monthly, saved: saved, severance: severance, pension: pension, total: total,
      totalRupiah: rate ? Math.round(total * rate) : null
    };
  }

  /* Kerja di hari libur nasional (관공서 공휴일): tempat kerja ≥5 pekerja wajib memberi libur berbayar.
     Jika tetap bekerja: upah libur (100%, kecuali pekerja bulanan yang sudah termasuk gaji) + upah kerja 150% (≤8 jam) / 200% (>8 jam). */
  function publicHolidayPay(opts) {
    var hourly = Math.max(0, +opts.hourly || 0);
    var hours = Math.max(0, +opts.hours || 0);
    var dailyHours = Math.max(0, opts.dailyHours == null ? 8 : +opts.dailyHours);
    var small = !!opts.smallWorkplace;
    var paidHoliday = small || opts.monthlySalaried ? 0 : Math.round(hourly * dailyHours);
    var workPay = small ? Math.round(hourly * hours)
      : Math.round(hourly * (Math.min(hours, 8) * 1.5 + Math.max(hours - 8, 0) * 2));
    return { paidHoliday: paidHoliday, workPay: workPay, total: paidHoliday + workPay };
  }

  var api = { RATES: RATES, unemployment: unemployment, publicHolidayPay: publicHolidayPay, dormDeductionLimit: dormDeductionLimit, savings: savings, deductions: deductions, monthlyPay: monthlyPay,
    severance: severance, pensionRefund: pensionRefund,
    weeklyHolidayPay: weeklyHolidayPay, annualLeave: annualLeave };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.Calc = api;
})(this);
