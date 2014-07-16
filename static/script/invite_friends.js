FB.init({
appId:'708254132555429',
cookie:true,
status:true,
xfbml:true
});

function FacebookInviteFriends()
{
FB.ui({
method: 'apprequests',
message: 'Join your frinds on best store from the world'
});
}
