import re
from astrbot.api import AstrBotConfig
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.message_components import Plain
from astrbot.api.star import Context, Star, register

@register("astrbot_plugin_thinktags", "长安某", "自定义过滤思考内容", "1.3.0")
class FilterthinktagsPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        # 将传入的配置对象保存在插件实例中
        self.config = config

    @filter.on_decorating_result()
    async def on_decorating_result(self, event: AstrMessageEvent):
        result = event.get_result()
        chain = result.chain

        # 从配置中读取要过滤的标签列表和开关状态
        # .get() 方法可以提供默认值，防止配置不存在时出错
        tags_to_filter = self.config.get('filtered_tags', [])
        should_filter_pattern = self.config.get('filter_thinking_pattern', True)

        new_chain = []
        for component in chain:
            # 只处理纯文本消息段
            if isinstance(component, Plain):
                new_text = component.text
                
                # 根据标签列表动态生成正则表达式并执行过滤
                # 仅在配置列表不为空时执行
                if tags_to_filter:
                    # 使用'|'连接所有标签名，构建正则表达式
                    # re.escape()可以防止用户输入的标签名包含特殊正则字符而导致错误
                    tag_group = '|'.join(re.escape(tag) for tag in tags_to_filter)
                    # 生成最终的匹配模式
                    pattern = rf'<({tag_group})>.*?</\1>\s*'
                    new_text = re.sub(pattern, new_text, flags=re.DOTALL)

                # 根据开关状态决定是否过滤 "Thinking: ..." 文本
                if should_filter_pattern:
                    new_text = re.sub(r'Thinking:\s*.*?(\n|$)', '', new_text, flags=re.DOTALL)
                
                # 清理文本两端的空白字符
                stripped_text = new_text.strip()
                # 只有当处理后的文本不为空时，才将其添加回新的消息链
                if stripped_text:
                    new_chain.append(Plain(stripped_text))
            else:
                # 如果不是纯文本组件（如图片、at等），则原样保留
                new_chain.append(component)

        # 用处理过的新消息链替换旧的消息链
        result.chain = new_chain
