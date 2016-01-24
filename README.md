# msohu-backup
题目要求：
写一个python脚本main.py，使用方式如下：
main.py -d 60 -u http://m.sohu.com -o /tmp/backup 

功能要求：
1、每60秒备份一次http://m.sohu.com这个页面，并按时间分隔保存在/tmp/backup目录下，如/tmp/backup/201601041325/；
2、用浏览器打开保存的页面时效果需要和线上的一致；
3、所有内容，包括图片，js，css等都需要存储在本地；
4、代码以github地址方式提交。

/tmp/backup/201601041325/这个目录的结构如下：
index.html  #html内容
images/  # 存放图片
js/  # 存放js
css/  # 存放css

完成过程：
    看到这个题目我的想法就是用正则表达式来获取html中的css,js,images的路径，把相应的内容保存在本地并修改原来html中对应的路径。
    沿着这个想法，首先观察了一下http://m.sohu.com这个网页的源码（chrome浏览器下，我发现这个网页在Firefox和chrome浏览器下显示的差异很大，不知道为什么），发现外链的css和js的html格式比较单一，但是图片的格式就比较多。经过分析，确定图片的正则匹配模式可以用三种来实现，详细匹配模式见代码。这个就完成了初步的一次备份。然后就实验性地跑了一遍，发现有些小的图标没有显示出来。通过审查元素进行分析，发现这些小图标的路径是在css中指定，于是又修改程序加上了修改css中图片路径的功能。这样之后，整个页面的显示看起来和原始网页一致了。
    接下来，我开始实现每60s备份一次的功能，我的想法是每次备份在子线程里完成，这样就不会影响主线程的计时的准确性了。最后采用了threading里的Timer()方法，可以很容易实现上述功能。
    然后，实现接收并处理输入的参数的功能。由于这个程序的参数处理比较简单，我采用的getopt模块的getopt()方法。
    最后，我对自己的代码进行了简单的重构，把一些重复使用的功能写成一个函数，统一一下一些变量命名，调一下格式，这样，整个程序就完成了。
    最后有两点疑问，希望您能解答一下。
    1、这个页面在我的Firefox浏览器和Chorme浏览器下显示差异很大，网页源码也不同，为什么？
    2、为什么这个页面中的外链的css和js都没有换行呢？尝试了各种方法都没有换行，用txt打开，用sublime打开，windows和linux都试过，还试过把所有\n替换为\r\n，然而都没有什么卵用，不换行给我分析css和js带来了困难。
    谢谢！
