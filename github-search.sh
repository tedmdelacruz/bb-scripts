cat $1 | awk '{print "https://github.com/search?q=%22"$0"%22&type=Code"}'
cat $1 | awk '{print "https://gist.github.com/search?q=%22"$0"%22&type=Code"}'
