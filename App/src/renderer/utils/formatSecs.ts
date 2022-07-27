export function formatSecs(secs: number) {
  let base = new Date(secs * 1000).toISOString().substring(11, 19);
  base = base.replace(/^(00:)+/g, '');
  base = base.indexOf(':') === -1 ? '0:' + base : base;
  return base[0] === '0' && base[1] !== ':' ? base.substring(1) : base;
}
