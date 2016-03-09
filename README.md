# SinaMicroblog_Creeper-Spider_VerificationCode
A creeper used to catch concerns and fans in sina microblog. It can imitate login. When encountered with verification code,it shall download the code and wait for the user to type in.新浪微博爬虫，获得每个用户和关注的，粉丝的用户id存入xml文件中，BFS，可以模拟登陆，模拟登陆中的验证码会抓取下来让用户输入

main.py中输入username中输入你的新浪微博账号,password中输入密码，下面的一串数字是你开始爬的用户id，验证码在veriImg.png图片中，若登陆过程中需要，按提示输入即可

目前新浪的模拟登陆过程是：先prelogin获取加密参数，然后用rsa吧之前获得的加密参数加密，然后login获取cookie（若需要验证码，此时login失败，返回验证码图片，再次post login请求），最后实现登陆

登陆完后就可以自由地urlopen了
