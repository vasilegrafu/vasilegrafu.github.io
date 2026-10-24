// Reads a Trainings question file (QB.addQuestions(chapter, [...])) and prints its questions as JSON,
// each with its chapter: node _trainings.cjs <questions/chNN.js>. The file is run in a context of its
// own, with a QB that keeps what addQuestions is given and ignores every other call.
const fs = require('fs');
const vm = require('vm');

const file = process.argv[2];
const found = [];
const QB = new Proxy({}, {
  get: (_, name) => name === 'addQuestions'
    ? (chapter, questions) => { for (const q of questions) found.push({ chapter, ...q }); }
    : () => {},
});
vm.runInNewContext(fs.readFileSync(file, 'utf8'), { QB }, { filename: file });
process.stdout.write(JSON.stringify(found));
