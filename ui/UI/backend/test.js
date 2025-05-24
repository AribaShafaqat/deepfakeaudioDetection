// testmail.js
require('dotenv').config();
const { sendOTP } = require('./utils/mfa');
sendOTP('aribashafaqatali@gmail.com', '123456');
