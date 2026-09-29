/* 페이지 공통: 숫자 입력 콤마 포맷, 원화 표시 */
function won(n) { return Math.round(n).toLocaleString('ko-KR') + '원'; }
function num(el) { return +String(el.value).replace(/[^0-9.]/g, '') || 0; }
document.querySelectorAll('input[data-money]').forEach(function (el) {
  el.addEventListener('input', function () {
    var v = el.value.replace(/[^0-9]/g, '');
    el.value = v ? (+v).toLocaleString('ko-KR') : '';
  });
});
