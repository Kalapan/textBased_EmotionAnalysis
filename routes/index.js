var express = require('express');
var router = express.Router();
var User = require('../models/user');
const {spawn} = require('child_process');
const e = require('express');
var dotenv = require('dotenv').config()

let userName = "";
let month = "01";
var emotionHappiness = 0;
var emotionDepression = 0;
var emotionAnger = 0;
var emotionAnxiety = 0;
var emotionNeutral = 0;
var emotionNeutral1 = 0;
var HappinessDisplay = [];

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
				emotionHappiness: emotionHappiness,
				HappinessDisplay: HappinessDisplay, 
				emotionDepression: emotionDepression, 
				emotionAnger: emotionAnger, 
				emotionAnxiety: emotionAnxiety, 
				emotionNeutral: emotionNeutral});
		}
	});
});

router.get('/logout', function (req, res, next) {
	console.log("logout")
	if (req.session) {
		// delete session object
		req.session.destroy(function (err) {
			if (err) {
				return next(err);
			} else {
				return res.redirect('/login');
			}
		});
	}
});

router.post('/update', function (req, res, next) {
	console.log("update")

	const childPython = spawn('python', ['python/tweetDownload.py', userName.twitter_id]);

	childPython.stdout.on('data', (data) => {
		console.log(`${data}`);
	});
	childPython.stderr.on('data', (data) => {
		console.log(`stderr: ${data}`);
	});
	childPython.on('close', (code) => {
		console.log(`child process exited with code ${code}`);
		return res.redirect('/profile');
	});
});

router.post('/monthSelection', function (req, res, next) {
	console.log("monthSelection")
	month = req.body.donut_select;
	console.log(req.body.donut_select);
	var MongoClient = require('mongodb').MongoClient;
	var url = process.env.MongoLogIn;
	MongoClient.connect(url, function(err, db) {
		if (err) throw err;
		var dbo = db.db("User");
		dbo.collection("tweets_information").find({
			Twitter_ID: userName.twitter_id,
			Month: month,
		}).project({
			_id: 0,
			Date: 1,
			Tweet: 1,
			Emotion: 1,
			Value: 1
		}).toArray(function(err, result) {
		  if (err) throw err;
		  	emotionHappiness = 0;
			emotionDepression = 0;
			emotionAnger = 0;
			emotionAnxiety = 0;
			emotionNeutral1 = 0;
			result.forEach(function(emotionType){
				if (emotionType.Emotion.includes("admiration") || emotionType.Emotion.includes("amusement") || emotionType.Emotion.includes("approval") || emotionType.Emotion.includes("caring") || emotionType.Emotion.includes("desire") || emotionType.Emotion.includes("excitement") || emotionType.Emotion.includes("gratitude") || emotionType.Emotion.includes("joy") || emotionType.Emotion.includes("love") || emotionType.Emotion.includes("optimism") || emotionType.Emotion.includes("pride") || emotionType.Emotion.includes("relief")) {
					emotionHappiness += 1;
					HappinessDisplay.push(emotionType);
					console.log(HappinessDisplay);
				} else if (emotionType.Emotion.includes("grief") || emotionType.Emotion.includes("remorse") || emotionType.Emotion.includes("sadness")) {
					emotionDepression += 1;
				} else if (emotionType.Emotion.includes("anger") || emotionType.Emotion.includes("annoyance") || emotionType.Emotion.includes("disappointment") || emotionType.Emotion.includes("disapproval") || emotionType.Emotion.includes("disgust")) {
					emotionAnger += 1;
				} else if (emotionType.Emotion.includes("embarrassment") || emotionType.Emotion.includes("fear") || emotionType.Emotion.includes("nervousness")) {
					emotionAnxiety += 1;
				} else {
					emotionNeutral1 += 1;
				}
			});
			db.close();
			emotionNeutral1 /= 2;
			emotionNeutral = Math.trunc(emotionNeutral1);
		});
	});
	setTimeout((() => {
		return res.redirect('/profile');
	  }), 1000)
});

router.get('/forgetpass', function (req, res, next) {
	res.render("forget.ejs");
});

router.post('/forgetpass', function (req, res, next) {
	User.findOne({email:req.body.email},function(err,data){
		console.log(data);
		if(!data){
			res.send({"Success":"This Email Is not regestered!"});
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