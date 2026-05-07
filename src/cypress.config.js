const {defineConfig} = require("cypress");

module.exports = defineConfig({
    e2e: {
        supportFile: false,
        setupNodeEvents(on, config) {
            // implement node event listeners here
        },
        baseUrl: "http://127.0.0.1:8050",
        video: false,
        screenshotOnRunFailure: false
    },
});
