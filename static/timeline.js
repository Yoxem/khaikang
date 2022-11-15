
timezoneChangingOne = (x)=>{var date= new Date(x.innerHTML);
    var year = date.getFullYear().toString();
    var month = (date.getMonth()+1).toString().padStart(2, '0');
    var day = date.getDate().toString().padStart(2, '0');
    var hour = date.getHours().toString().padStart(2, '0');
    var min = date.getMinutes().toString().padStart(2, '0');
    var sec = date.getSeconds().toString().padStart(2, '0');
    local_date_string = `${year}-${month}-${day} ${hour}:${min}:${sec}`;
    x.innerHTML=local_date_string;}

function timezoneChanging(){
document.querySelectorAll(".post-time").forEach(
x => timezoneChangingOne(x)
    );
}



$name = (x) => document.getElementsByName(x);
$ = (x) => document.getElementById(x);
var httpRequest;
$("submit_post").addEventListener('click', make_req);

async function make_req() {

post_text = $('post_text').value;
post_privilage = $('privil_choosing').value;

if (post_text != ""){

await fetch('/api/post', {
method: 'POST',
headers: {
"X-CSRFToken": "{{ csrf_token }}",
'Content-Type': 'application/json',
},
body: JSON.stringify({
"privilage" : post_privilage,
"text": post_text,
})

}).then(response => {if (response.ok == true)
{$('post_text').value = "";
getLatestPosts(); // wait for a moment then get latest posts
}}

);
}



}

function auto_expand(element) {
element.style.height = 6+"em";
element.style.height = (element.scrollHeight)+"px";
}

timezoneChanging();

function adjust_post_text(){
var post_text = $("post_text");
post_text.style.height = 6+"em";
post_text.style.height = (post_text.scrollHeight)+"px";
}


async function getRecentPostsCounter(){
latest_time_string = $("latest_time").innerHTML;
await fetch('/api/get_recent_posts_counter', {
method: 'POST',
headers: {
"X-CSRFToken": "{{ csrf_token }}",
'Content-Type': 'application/json',
},
body: JSON.stringify({
"latest_time" : latest_time_string,
})

}).then(response => response.json())
.then(the_json => {console.log(the_json);let newer_posts_num = the_json['newer_posts_num'];
if (newer_posts_num == 1)
{   $("new_post_notifier").style.display = "block";
$("new_post_notifier").innerHTML = `1 new post`}
if (newer_posts_num > 1)
{   $("new_post_notifier").style.display = "block";
$("new_post_notifier").innerHTML = `${newer_posts_num} new posts`} });

}

var intervalID = window.setInterval(getRecentPostsCounter, 20000);

function appendPostToTheEnd(post){
var public_tl = $("public_timeline");
var new_div = createPostDiv(post);


public_tl.insertBefore(new_div, $('previous_post_loader'));
}

async function getPreviousPosts(){
var new_oldest_time;
oldest_time_string = $("oldest_time").innerHTML;
await fetch('/api/get_previous_posts', {
method: 'POST',
headers: {
"X-CSRFToken": "{{ csrf_token }}",
'Content-Type': 'application/json',
},
body: JSON.stringify({
"oldest_time" : oldest_time_string,
}) }).then(response => response.json())
.then(item => {new_oldest_time_raw = item['oldest_time'];
        new_oldest_time =  new_oldest_time_raw.substring(0,10) + " " + new_oldest_time_raw.substring(11,26) + "+0000";
        return item['older_posts'];})
.then(posts => {if (posts.length == 0)
        {$('previous_post_loader').style.display = 'none';}
        else{posts.forEach(post => appendPostToTheEnd(post));
                    $('oldest_time').innerHTML = new_oldest_time;}})
}


async function getLatestPosts(){
latest_time_string = $("latest_time").innerHTML;
await fetch('/api/get_latest_posts', {
method: 'POST',
headers: {
"X-CSRFToken": "{{ csrf_token }}",
'Content-Type': 'application/json',
},
body: JSON.stringify({
"latest_time" : latest_time_string,
}) }).then(response => response.json())
.then(item => item['newer_posts'])
.then(posts => {posts.forEach(post => addPostToTheBeginning(post));
$('new_post_notifier').style.display = "none";
var nowTime = new Date();
var nowTimeString = nowTime.toISOString();
$("latest_time").innerHTML = nowTimeString.substring(0,10) + " " + nowTimeString.substring(11,23) + "000+0000"; });
}

function createPostDiv(post){

var new_div = document.createElement("div");
new_div.id =  `post-${post.id}`;
new_div.className = "post";
post_text_replaced = post.text.replace(/(\r\n|\n\r|\r|\n)/g, "<br>" );
console.log(post_text_replaced);
new_div.innerHTML = `<a href="/user/${post.poster_username}">${post.poster_shown_name}</a>
at <a href="/post/${post.id}" class="post-time">${post.post_time}</a><br>
${post_text_replaced}<br>
<span id="reply-${post.id}" value="${post.id}" class="reply">↩️</span>
- <span id="repost-${post.id}" value="${post.id}" class="repost">🔁</span> 
- <span id="fav-${post.id}" value="${post.id}" class="fav">⭐</span>`;

new_div_timestamp = new_div.getElementsByClassName('post-time')[0];

timezoneChangingOne(new_div_timestamp);

return new_div;
}

function addPostToTheBeginning(post){
var public_tl = $("public_timeline");
var new_div = createPostDiv(post);


public_tl.insertBefore(new_div, $('latest_time').nextSibling);

}

$("new_post_notifier").addEventListener('click', getLatestPosts);
$("previous_post_loader").addEventListener('click', getPreviousPosts);



adjust_post_text();