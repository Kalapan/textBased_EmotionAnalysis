var express = require('express');
var router = express.Router();
var User = require('../models/user');
const {spawn} = require('child_process');
const e = require('express');
var dotenv = require('dotenv').config()

let date_ob = new Date();
let userName = "";
let month = ("0" + (date_ob.getMonth() + 1)).slice(-2);
let year = date_ob.getFullYear();
var emotionHappiness = 0, emotionDepression = 0, emotionAnger = 0, emotionAnxiety = 0, emotionNeutral = 0;
var HappinessDisplay = [], depressionDisplay = [], angerDisplay = [], anxietyDisplay = [], neutralDisplay = [];
var Happiness = [], depression = [], anger = [], anxiety = [], neutral = [];

function resetVals() {
	emotionHappiness = 0, emotionDepression = 0, emotionAnger = 0, emotionAnxiety = 0, emotionNeutral = 0;
	HappinessDisplay = [], depressionDisplay = [], angerDisplay = [], anxietyDisplay = [], neutralDisplay = [];
	Happiness = [], depression = [], anger = [], anxiety = [], neutral = [];
}

router.get('/', function (req, res, next) {
	return res.render('index.ejs');
});

router.post('/', function(req, res, next) {
	console.log(req.body);
	var personInfo = req.body;
	if(!personInfo.email || !personInfo.password || !personInfo.passwordConf){
		res.send();
	} else {
		if (personInfo.password == personInfo.passwordConf) {

			User.findOne({email:personInfo.email},function(err,data){
				if(!data){
					var c;
					User.findOne({},function(err,data){
						if (data) {
							console.log("if");
							c = data.unique_id + 1;
						}else{
							c=1;
						}
						var newPerson = new User({
							unique_id:c,
							email:personInfo.email,
							twitter_id:personInfo.twitter_id,
							password: personInfo.password,
							passwordConf: personInfo.passwordConf
						});
						newPerson.save(function(err, Person){
							if(err)
								console.log(err);
							else
								console.log('Success');
						});
						for (let i = 1; i <= 1; i++) {
							const args = ("0" + (i)).slice(-2);
							const childPython = spawn('python', ['python/tweetDownload2.py', personInfo.twitter_id, args]);
						  
							childPython.stdout.on('data', (data) => {
							  console.log(`stdout ${i}: ${data}`);
							});
						  
							childPython.stderr.on('data', (data) => {
							  console.error(`stderr ${i}: ${data}`);
							});
						  
							childPython.on('close', (code) => {
							  console.log(`child process ${i} exited with code ${code}`);
							});
						  }
					}).sort({_id: -1}).limit(1);
					res.send({"Success":"You have been registered."});
				}else{
					res.send({"Success":"Email is already used."});
				}
			});
		}else{
			res.send({"Success":"Passwaord does not match."});
		}
	}
});

router.get('/login', function (req, res, next) {
	return res.render('login.ejs');
});

router.post('/login', function (req, res, next) {
	//console.log(req.body);
	User.findOne({email:req.body.email},function(err,data){
		if(data){
			
			if(data.password==req.body.password){
				//console.log("Done Login");
				req.session.userId = data.unique_id;
				//console.log(req.session.userId);
				res.send({"Success":"Success!"});
				
			}else{
				res.send({"Success":"Wrong password!"});
			}
		}else{
			res.send({"Success":"This Email Is not regestered!"});
		}
	});
});

router.get('/profile', function (req, res, next) {
	console.log("profile");
	User.findOne({unique_id:req.session.userId},function(err,data){
		console.log("data");
		console.log(data);
		if(!data){
			res.redirect('/');
		}else{
			userName = {"twitter_id":data.twitter_id};
			return res.render('data.ejs', {
				name:userName.twitter_id,
				month: month,
				year: year,
				emotionHappiness: emotionHappiness,
				HappinessDisplay: HappinessDisplay,
				emotionDepression: emotionDepression, 
				depressionDisplay: depressionDisplay,
				emotionAnger: emotionAnger,
				angerDisplay: angerDisplay, 
				emotionAnxiety: emotionAnxiety, 
				anxietyDisplay: anxietyDisplay,
				emotionNeutral: emotionNeutral,
				neutralDisplay: neutralDisplay});
		}
	});
});

router.get('/logout', function (req, res, next) {
	console.log("logout")
	if (req.session) {
		req.session.destroy(function (err) {
			if (err) {
				return next(err);
			} else {
				userName = "";
				month = ("0" + (date_ob.getMonth() + 1)).slice(-2);
				year = date_ob.getFullYear();
				resetVals();
				return res.redirect('/login');
			}
		});
	}
});

router.post('/update', function (req, res, next) {
	console.log("update")
	for (let i = 1; i <= 4; i++) {
		const args = ("0" + (i)).slice(-2);
		const childPython = spawn('python', ['python/tweetDownload2.py', userName.twitter_id, args]);
	  
		childPython.stdout.on('data', (data) => {
		  console.log(`stdout ${i}: ${data}`);
		});
	  
		childPython.stderr.on('data', (data) => {
		  console.error(`stderr ${i}: ${data}`);
		});
	  
		childPython.on('close', (code) => {
		  console.log(`child process ${i} exited with code ${code}`);
		});
	  }
});

router.post('/dateSelect', function (req, res, next) {
	console.log("dateSelect")
	month = req.body.month_select;
	year = req.body.year_select;
	console.log(req.body.month_select);
	console.log(req.body.year_select);
	var MongoClient = require('mongodb').MongoClient;
	var url = process.env.MongoLogIn;
	MongoClient.connect(url, function(err, db) {
		if (err) throw err;
		var dbo = db.db("User");
		dbo.collection("tweets_information").find({
			Twitter_ID: userName.twitter_id,
			Month: month,
			Year: year,
		}).project({
			_id: 0,
			Twitter_ID: 1,
			Date: 1,
			Month: 1,
			Tweet: 1,
			Emotion: 1,
			Value: 1
		}).toArray(function(err, result) {
		  if (err) throw err;
		  resetVals();
			result.forEach(function(emotionType){
				if (emotionType.Emotion.includes("admiration") || emotionType.Emotion.includes("amusement") || emotionType.Emotion.includes("approval") || emotionType.Emotion.includes("caring") || emotionType.Emotion.includes("desire") || emotionType.Emotion.includes("excitement") || emotionType.Emotion.includes("gratitude") || emotionType.Emotion.includes("joy") || emotionType.Emotion.includes("love") || emotionType.Emotion.includes("optimism") || emotionType.Emotion.includes("pride") || emotionType.Emotion.includes("relief")) {
					emotionHappiness += 1;
					Happiness.push(emotionType);
					HappinessDisplay = JSON.stringify(Happiness);
				} else if (emotionType.Emotion.includes("grief") || emotionType.Emotion.includes("remorse") || emotionType.Emotion.includes("sadness")) {
					emotionDepression += 1;
					depression.push(emotionType);
					depressionDisplay = JSON.stringify(depression);
				} else if (emotionType.Emotion.includes("anger") || emotionType.Emotion.includes("annoyance") || emotionType.Emotion.includes("disappointment") || emotionType.Emotion.includes("disapproval") || emotionType.Emotion.includes("disgust")) {
					emotionAnger += 1;
					anger.push(emotionType);
					angerDisplay = JSON.stringify(anger);
				} else if (emotionType.Emotion.includes("embarrassment") || emotionType.Emotion.includes("fear") || emotionType.Emotion.includes("nervousness")) {
					emotionAnxiety += 1;
					anxiety.push(emotionType);
					anxietyDisplay = JSON.stringify(anxiety);
				} else {
					emotionNeutral += 1;
					neutral.push(emotionType);
					neutralDisplay = JSON.stringify(neutral);
				}
			});
			db.close();
		});
	});
	setTimeout((() => {
		return res.redirect('/profile');
	  }), 1500)
});

router.get('/forgetpass', function (req, res, next) {
	res.render("forget.ejs");
});

router.post('/forgetpass', function (req, res, next) {
	User.findOne({email:req.body.email},function(err,data){
		console.log(data);
		if(!data){
			res.send({"Success":"This Email is not regestered!"});
		}else{
			if (req.body.password==req.body.passwordConf) {
			data.password=req.body.password;
			data.passwordConf=req.body.passwordConf;

			data.save(function(err, Person){
				if(err)
					console.log(err);
				else
					console.log('Success');
					res.send({"Success":"Password changed!"});
			});
		}else{
			res.send({"Success":"Password does not matched! Both Password should be same."});
		}
		}
	});
	
});

module.exports = router;