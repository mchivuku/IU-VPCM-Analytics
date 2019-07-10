<?php
/*** Example .apiconfig file ******  
[twitter]
twitteruser = "iupui"
notweets = 30
consumerkey = "7hsN3fzOUXVypMDn53OPg"
consumersecret = "mRGwLsst7bFcOy0n7UcLlJEoCyVCYfij6vYZSXus"
accesstoken = "10086382-9fMeqrOtCn1CQd5qVLnsRhaNUrUc0z9u0xFwYTJz5"
accesstokensecret = "Nwgl7BGdymS0NmSE4NWEFDCFaDB6zOqWNXrZay3vZzs"
require_once 'iet/CFG.php';
require_once("php/twitteroauth/twitteroauth.php");
***/

require 'php/twitteroauth/twitteroauth.php';
require 'iet/CFG.php';

mb_internal_encoding('UTF-8');

class TwitterFeed extends CFG {
    function __construct($id='twitter', $cfgfile='.apiconfig') {
		parent::__construct($id, $cfgfile);
		$twitteruser = $this->twitteruser;
                $notweets = $this->notweets;
                $list = isset($this->list) ? $this->list : '';
		$this->tweets = $this->getTweets($twitteruser, $notweets, $list);
		if($this->tweets) $processedTweets = $this->processTweets($this->tweets);
		if($processedTweets=='' || $processedTweets=='null' || $this->tweets{0}->created_at=='') {
			$message = '';
			
			$headers = 'From: pagr-twitter-api@iu.edu'."\r\n";
      			$headers .= 'Cc:mercerjd@iu.edu'."\r\n";
			$message .= 'ORIGINAL FEED: '.$this->tweets."\r\n";
			$message .= 'PROCESSED FEED: '.$processedTweets."\r\n";;
			mail('mbcalver@iu.edu', 'Twitter/JSON Error on PAGRIET', $message, $headers);

			$logText = date()." - ".$message."\r\n";
			$fp = fopen('/ip/pagriet/bin/logs/twitterfeed.txt', 'a');
			fwrite($fp, $logText);
			fclose($fp);
		}
    }
    
    function getTweets($twitteruser='',$notweets=200, $list) {
		$connection = new TwitterOAuth($this->consumerkey, $this->consumersecret, $this->accesstoken, $this->accesstokensecret);
		if($list!='') {
			$tweets = $connection->get("https://api.twitter.com/1.1/lists/statuses.json?slug=".$list."&owner_screen_name=".$twitteruser."&count=".$notweets);
		}
		else {
			$tweets = $connection->get("https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=".$twitteruser."&count=".$notweets);
		}
		return $tweets;
    }

    function processTweets(&$tweets) {
		$keepers = array();
		foreach($tweets as $i=>$tweet) {

		    if($tweet->in_reply_to_screen_name!='' && $tweet->in_reply_to_screen_name!=null) continue;

		    $isRetweet = isset($tweet->retweeted_status);
		    if($isRetweet) {
			$theTweet = $tweet->retweeted_status->text;
			$entities = $tweet->retweeted_status->entities;
		    }
		    else {
			$theTweet = $tweet->text;
			$entities = $tweet->entities;
		    }


		    $r = array();
		    if($entities->hashtags) {
			foreach($entities->hashtags as $hashtag) {
			    $s = $hashtag->indices[0];
			    $e = $hashtag->indices[1];
			    $t = $hashtag->text;
			    $h = "https://twitter.com/hashtag/$t?src=hash";
			    $r[] = array('start'=>$s, 'end'=>$e, 'text'=>$t, 'href'=>$h, 'type'=>'hashtag');
			}	
		    }
		    
		    if(isset($entities->media)) {
			foreach($entities->media as $m) {
			    $s = $m->indices[0];
			    $e = $m->indices[1];
			    $t = $m->url;
			    $h = $m->url;
			    $r[] = array('start'=>$s, 'end'=>$e, 'text'=>$t, 'href'=>$h, 'type'=>'media');
			}
		    }
		    
		    if($entities->urls) {
			foreach($entities->urls as $u) {
			    $s = $u->indices[0];
			    $e = $u->indices[1];
			    $t = $u->url;
			    $h = $u->url;
			    $r[] = array('start'=>$s, 'end'=>$e, 'text'=>$t, 'href'=>$h, 'type'=>'url');
			}
		    }

		    if($entities->user_mentions) {
			foreach($entities->user_mentions as $u) {
			    $s = $u->indices[0];
			    $e = $u->indices[1];
			    $t = $u->screen_name;
			    $h = "https://twitter.com/hashtag/$t?src=hash";
			    $h = "https://twitter.com/$t";
			    $r[] = array('start'=>$s, 'end'=>$e, 'text'=>$t, 'href'=>$h, 'type'=>'url');
			}
		    }

		    if($entities->symbols) {
			foreach($entities->symbols as $u) {
			    $s = $u->indices[0];
			    $e = $u->indices[1];
			    #$t = $u->url;
			    #$h = $u->url;
			    #$r[] = array('start'=>$s, 'end'=>$e, 'text'=>$t, 'href'=>$h, 'type'=>'url');
			}
		    }

		    uasort($r, array($this, 'sortIndices')); 

		    foreach($r as $rr) {
			$token = ($rr['type']=='hashtag') ? '#' : '';
			if($rr['type']=='url') $rr['text'] = mb_substr($theTweet, $rr['start'], $rr['end']-$rr['start']);
			$link = '<a href="' . $rr['href'] . '">' . $token . $rr['text'] . '</a>';
			$theTweet = $this->str_replace_segment($theTweet, $rr['start'], $rr['end'], $link, $rr['type']);
		    }	
		    if($isRetweet) {
			$theUser = $tweet->retweeted_status->user->screen_name;
			$link = "<a href=\"https://twitter.com/$theUser\">@$theUser</a>";
			$theTweet = "RT $link: $theTweet";
		    }
		    
		    $tweets[$i]->prettyTweet = utf8_encode($theTweet);
		    $tweets[$i]->prettyTweetNoUTF8 = $theTweet;
		    $keepers[] = $tweet;
		}	
		return $keepers;
    }

    function str_replace_segment($source, $s, $e, $to) {
		$front = mb_substr($source, 0, $s);
		$back = mb_substr($source, $e);
		$result = "$front$to$back";

		#echo '<pre>';
		#var_dump($source, $s, $e, $to, $result, $front, $back);
		return $result;
    }
    
    function sortIndices($a, $b) {
		if($a['start'] < $b['start']) return 1;
		if($a['start'] > $b['start']) return -1;
		return 0;
    }

    function toJson() {
		return json_encode($this->tweets);
    }

    function __toString() {
		return json_encode($this->tweets);
    }

}