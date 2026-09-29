/* Umum: format angka dengan titik ribuan, tampilan Won/Rupiah */
function won(n) { return '₩' + Math.round(n).toLocaleString('id-ID'); }
function minus(n) { return n > 0 ? '− ' + won(n) : won(0); }
function rp(n) { return 'Rp' + Math.round(n).toLocaleString('id-ID'); }
function num(el) {
  if (el.type === 'number') return +el.value || 0;
  // Format Indonesia: titik = ribuan, koma = desimal
  return +String(el.value).replace(/[^0-9,]/g, '').replace(',', '.') || 0;
}
document.querySelectorAll('input[data-money]').forEach(function (el) {
  el.addEventListener('input', function () {
    var v = el.value.replace(/[^0-9]/g, '');
    el.value = v ? (+v).toLocaleString('id-ID') : '';
  });
});
