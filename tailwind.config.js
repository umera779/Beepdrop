// /** @type {import('tailwindcss').Config} */
// module.exports = {
//   content: [],
//   theme: {
//     extend: {},
//   },
//   plugins: [],
// }

module.exports = {
  darkMode: 'class',
  content: [
    './templates/**/*.html', // Include all your Django templates
    './static/**/*.js',      // Include JavaScript files in your static dir
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
