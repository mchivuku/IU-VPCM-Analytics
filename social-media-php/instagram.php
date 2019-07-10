<?php
// Look up your id here:http://jelled.com/instagram/lookup-user-id#
/*** REQUIRES THE FOLLOWING LOCAL .apiconfig file 
[instagram]
id = "285339596"
client_id = "5e5b7639ae07477785b1fbb08c5e98ed"
client_secret = "4f926e867c054f5b96c74199eab30a44"
website_url = "https://www.iu.edu/~pagriet/mercerjd/instagram/instagram.php"
redirect_uri = "https://www.iu.edu/~pagriet/mercerjd/instagram/instagram.php"
scope = 'likes+comments'
#code = "3595e6fb2ee8490f88e5092561c95d17"
#access_token = "285339596.5e5b763.fa14c6a900c14349a30fa3e512027992"
*************************************************************************************/

#*** INSTAGRAM CLIENT **********************************************************
require_once 'iet/CURLClient.php';

class InstagramClient extends CURLClient {
  private $useSession  = false;
  function __construct() {
    $ini = parse_ini_file('.apiconfig', true);
    $cfg = $ini['instagram'];
    foreach($cfg as $k=>$v) $this->{$k} = $v;

    if($this->useSession) {
      save_session_path("{$_ENV['HOME']}/_sess");
      session_start();
    }
    
    if(isset($_SESSION['access_token'])) $this->go($_SESSION['access_token']);
    else if(isset($_GET['access_token'])) $this->go($_GET['access_token']);
    else if(isset($this->access_token)) $this->go($this->access_token);
    else if(isset($this->code)) $this->getAccessToken($this->code);
    else if(isset($_GET['code'])) $this->getAccessToken($_GET['code']);
    else $this->getCode();
  }

  function getCode() {
    $url = 'https://api.instagram.com/oauth/authorize/?';
    $params = array();
    $params['client_id'] = $this->client_id;
    $params['redirect_uri'] = $this->redirect_uri;
    $params['response_type'] = 'code';
    #$params['scope'] = '';
    #$params['scope'] = 'likes+comments';
    if(isset($this->scope)) $params['scope'] = $this->scope;
    foreach($params as $k=>$v) $args[] = "$k=$v";
    $url .= implode('&', $args);

    #echo "<a href=\"$url\">Click here</a>";
    header("Location: $url\r\n\r\n");
  }

  function getAccessToken($code) {
    # trade code for access token
    $url = 'https://api.instagram.com/oauth/access_token?';
    $params = array();
    $params['client_id'] = $this->client_id;
    $params['client_secret'] = $this->client_secret;
    $params['grant_type'] = 'authorization_code';
    $params['redirect_uri'] = $this->redirect_uri;
    $params['code'] = $code;

    $response = $this->post($url, $params);
    $response = json_decode($response);

    $this->access_token = $response->access_token;
    $this->username = $response->user->username;
    $this->bio = $response->user->bio;
    $this->website = $response->user->website;
    $this->profile_picture = $response->user->profile_picture;
    $this->full_name = $response->user->full_name;
    $this->id = $response->user->id;

    if($this->useSession) {
      $_SESSION['access_token'] = $response->access_token;
      $_SESSION['username'] = $response->user->username;
      $_SESSION['bio'] = $response->user->bio;
      $_SESSION['website'] = $response->user->website;
      $_SESSION['profile_picture'] = $response->user->profile_picture;
      $_SESSION['full_name'] = $response->user->full_name;
      $_SESSION['id'] = $response->user->id;
    }
    
    #echo '<pre>';
    #var_dump($this, $response);
    #echo '</pre>';

    $this->go($this->access_token);
  }

  function go($access_token) {
    $url = "https://api.instagram.com/v1/users/{$this->id}/media/recent?";
    $params = array('access_token'=>$access_token);

    $response = $this->get($url, $params);
    $pics = json_decode($response, true);

    echo '<pre>' . print_r($response, true) . '</pre>';


    // display the url of the last image in standard resolution
    echo $pics['data'][0]['images']['standard_resolution']['url'];
  }

}