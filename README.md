# First Log Parser
Log parser for First project

##使用环境
1. python 2.75
2. First项目输出的日志文件
3. 配置文件config.xml

##使用方法
1. 配置文件  
	* start标签表示配对log中开始的那一条中**必然包含**的关键字（用于搜索开始log）
	* end标签与start配对试用，存储配对log中结束那一条中**必然包含**的关键字
	* signature标签存储配对的start log 和 end log中同时必然包含的关键字的**索引值范围**，即相对于log message开始位置，例如log message为`webkit:(0x11011)`其中`0x11011`为signature，那么在配置文件的signature标签中描述为`8,15`
	* 配置文件应保存为config.xml存储在parser.py所在目录下，格式如下：

```xml
<config>
	<item>
		<start>xxx start</start>
		<end>xxx end</end>
		<signature>8,15</signature>
	</item>
</config>	
```
2. 使用如下命令  

```c
	python parser -i logfile -o outputfile
```  
* -i 参数为日志文件名
* -o 参数为保存分析结果的文件名