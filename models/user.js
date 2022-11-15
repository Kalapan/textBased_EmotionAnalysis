var mongoose = require('mongoose');
var Schema = mongoose.Schema;

userSchema = new Schema( {
	
	unique_id: Number,
	email: String,
	twitter_id: String,
	password: String,
	passwordConf: String
}),
User = mongoose.model('user_credentials', userSchema);

module.exports = User;