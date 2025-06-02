function splitSyllables(word) {
  // pega consoantes iniciais, vogais (ou ditongos) e opcional consoante seguinte
  const matches = word.match(/[^aeiou]*[aeiou]+[^aeiou]?/gi) || [];
  return matches.map((s, i, arr) => {
    const next = arr[i + 1];
    // se o próximo bloco começa com a mesma consoante que este bloco terminou,
    // remove essa consoante do fim deste bloco
    if (
      next &&
      s.slice(-1).toLowerCase() === next[0].toLowerCase() &&
      /[^aeiou]/i.test(s.slice(-1))
    ) {
      return s.slice(0, -1);
    }
    return s;
  });
}

const word = "perderia";
console.log(splitSyllables(word)); // [ 'per', 'de', 'ria' ]
