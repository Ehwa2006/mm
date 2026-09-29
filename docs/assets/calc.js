/* 2026년 기준 급여 계산 로직. 브라우저(window.Calc)와 Node(require) 양쪽에서 사용. */
(function (root) {
  var RATES = {
    year: 2026,
    pension: 0.0475,            // 국민연금 근로자 부담 (총 9.5%)
    pensionMin: 410000,         // 기준소득월액 하한 (2026.7~2027.6)
    pensionMax: 6590000,        // 기준소득월액 상한 (2026.7~2027.6)
    health: 0.03595,            // 건강보험 근로자 부담 (총 7.19%)
    longTermCare: 0.9448 / 7.19, // 장기요양 = 건강보험료 × (0.9448% / 7.19%)
    employment: 0.009,          // 고용보험 근로자 부담
    minimumWage: 10320,         // 2026 최저시급
    monthlyHours: 209           // 주 40시간 + 주휴 기준 월 소정근로시간
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

  function childTaxCredit(children) {
    if (children <= 0) return 0;
    if (children === 1) return 150000;
    if (children === 2) return 350000;
    return 350000 + (children - 2) * 300000;
  }

  /* 연봉 실수령액 (연 단위 세액을 추정해 월로 나눈 근사치) */
  function salary(opts) {
    var annual = Math.max(0, +opts.annual || 0);
    var nonTaxMonthly = Math.max(0, +opts.nonTaxMonthly || 0);
    var dependents = Math.max(1, Math.floor(+opts.dependents || 1));
    var children = Math.max(0, Math.floor(+opts.children || 0));

    var monthlyGross = annual / 12;
    var taxableMonthly = Math.max(0, monthlyGross - nonTaxMonthly);
    var taxableAnnual = taxableMonthly * 12;

    var pensionBase = Math.min(Math.max(taxableMonthly, RATES.pensionMin), RATES.pensionMax);
    var pension = taxableMonthly > 0 ? floor10(pensionBase * RATES.pension) : 0;
    var health = floor10(taxableMonthly * RATES.health);
    var care = floor10(health * RATES.longTermCare);
    var employment = floor10(taxableMonthly * RATES.employment);

    var incomeAmount = taxableAnnual - earnedIncomeDeduction(taxableAnnual);
    var taxBase = incomeAmount - 1500000 * dependents - (pension + health + care + employment) * 12;
    var computed = progressiveTax(Math.max(0, taxBase));
    var credits = earnedIncomeTaxCredit(computed, taxableAnnual) + 130000 + childTaxCredit(children);
    var annualTax = Math.max(0, computed - credits);
    var incomeTax = floor10(annualTax / 12);
    var localTax = floor10(incomeTax * 0.1);

    var deductions = pension + health + care + employment + incomeTax + localTax;
    return {
      monthlyGross: Math.round(monthlyGross),
      pension: pension, health: health, longTermCare: care, employment: employment,
      incomeTax: incomeTax, localTax: localTax,
      totalDeductions: deductions,
      monthlyNet: Math.round(monthlyGross - deductions),
      annualNet: Math.round((monthlyGross - deductions) * 12)
    };
  }

  /* 주휴수당: 주 15시간 이상 근무 시 (주 소정근로시간/40 × 8시간) × 시급 */
  function weeklyHolidayPay(opts) {
    var hourly = Math.max(0, +opts.hourly || 0);
    var hours = Math.max(0, +opts.weeklyHours || 0);
    var eligible = hours >= 15;
    var holidayHours = eligible ? Math.min(hours, 40) / 40 * 8 : 0;
    var weeklyPay = Math.round(holidayHours * hourly);
    var weeksPerMonth = 365 / 7 / 12;
    return {
      eligible: eligible,
      holidayHours: Math.round(holidayHours * 100) / 100,
      weeklyHolidayPay: weeklyPay,
      weeklyTotal: Math.round(hours * hourly) + weeklyPay,
      monthlyTotal: Math.round((hours + holidayHours) * hourly * weeksPerMonth),
      belowMinimum: hourly > 0 && hourly < RATES.minimumWage
    };
  }

  function parseDate(s) {
    var p = String(s).split('-').map(Number);
    return new Date(Date.UTC(p[0], p[1] - 1, p[2]));
  }
  function daysBetween(a, b) { return Math.round((b - a) / 86400000); }

  /* 퇴직금: 1일 평균임금 × 30일 × (재직일수 / 365). lastDay는 마지막 근무일. */
  function severance(opts) {
    var start = parseDate(opts.startDate);
    var retire = parseDate(opts.lastDay);
    retire.setUTCDate(retire.getUTCDate() + 1); // 퇴직일 = 마지막 근무일 다음날
    var tenureDays = daysBetween(start, retire);
    var from = new Date(retire);
    from.setUTCMonth(from.getUTCMonth() - 3);
    var periodDays = daysBetween(from, retire);
    var wages3m = Math.max(0, +opts.wages3m || 0)
      + Math.max(0, +opts.annualBonus || 0) * 3 / 12
      + Math.max(0, +opts.annualLeavePay || 0) * 3 / 12;
    var avgDaily = periodDays > 0 ? wages3m / periodDays : 0;
    var eligible = tenureDays >= 365;
    return {
      eligible: eligible,
      tenureDays: tenureDays,
      periodDays: periodDays,
      averageDailyWage: Math.round(avgDaily),
      severancePay: eligible ? Math.round(avgDaily * 30 * tenureDays / 365) : 0
    };
  }

  /* 시급·월급·연봉 상호 변환 (주 40시간, 월 209시간 기준) */
  function convertWage(opts) {
    var amount = Math.max(0, +opts.amount || 0);
    var hourly;
    if (opts.from === 'hourly') hourly = amount;
    else if (opts.from === 'monthly') hourly = amount / RATES.monthlyHours;
    else hourly = amount / 12 / RATES.monthlyHours;
    var monthly = hourly * RATES.monthlyHours;
    return {
      hourly: Math.round(hourly),
      monthly: Math.round(monthly),
      annual: Math.round(monthly * 12),
      belowMinimum: hourly > 0 && hourly < RATES.minimumWage,
      minimumMonthly: RATES.minimumWage * RATES.monthlyHours
    };
  }

  var api = { RATES: RATES, salary: salary, weeklyHolidayPay: weeklyHolidayPay,
    severance: severance, convertWage: convertWage };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.Calc = api;
})(this);
