# 课题4：同步转异步组件 #
## 组件说明和要求： ##

1. 背景描述：在实际⽣产环境，请求响应交互模式⽆法满⾜耗时较⻓的批处理型接⼝需求，基础设施⼀般在F5、IDC入口、DMZ与业务核⼼⽹间等部署了防⽕墙，⽬前防⽕墙最多能保持不活跃连接30分钟，超过30分钟就会回收端⼝，意味着只要接⼝响应时间超过30分钟，都会受到影响。因此，我们需要提供同步转异步调⽤的能⼒。
2. 组件的能⼒描述
	- ⽀持任务异步处理，接收到同步请求后转为异步任务执⾏；
	- ⽀持任务http回调、MQ通知，消费者要提供选择回调的机制和接⼝；
	- ⽀持任务状态查询和处理结果查询；
	- ⽀持持久化，⽅便任务的状态更新、历史流⽔查询；
	- ⽀持集群，通过集群提升组件的并发处理能⼒；
