
module.exports = {
  root: true,
  "globals": {
    "pagePopupShow": false
},
  parserOptions: {
    parser: 'babel-eslint'
  },
  env: {
    browser: true,
  },
  extends: [
    'plugin:vue/essential', 
    'standard'
  ],
  plugins: [
    'vue'
  ],
  rules:{
    "indent": [
      "error",
      4
    ],
    "semi": [2, "always"],
    "no-debugger": process.env.NODE_ENV === "production" ? "error" : "off",
    "no-useless-escape": 0
  },
}
