import re
from astrbot.api import AstrBotConfig
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.message_components import Plain
from astrbot.api.star import Context, Star, register

@register("astrbot_plugin_thinktags", "长安某", "过滤标签和文本", "1.3.0")
class FilterthinktagsPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        # 将传入的配置对象保存在插件实例中
        self.config = config

    @filter.on_decorating_result()
    async def on_decorating_result(self, event: AstrMessageEvent):
        result = event.get_result()
        chain = result.chain

        # 从配置中读取两个列表，如果配置不存在则使用空列表作为默认值
        tags_to_filter = self.config.get('filtered_tags', [])
        prefixes_to_filter = self.config.get('filtered_prefixes', [])

        new_chain = []
        for component in chain:
            # 只处理纯文本消息段
            if isinstance(component, Plain):
                new_text = component.text
                

                # 根据标签列表动态过滤标签
                if tags_to_filter:
                    tag_group = '|'.join(re.escape(tag) for tag in tags_to_filter)
                    pattern = rf'<({tag_group})>.*?</\1>\s*'
                    new_text = re.sub(pattern, new_text, flags=re.DOTALL)

                # 过滤无标签的、可能跨行的文本块
                if prefixes_to_filter:
                    for prefix in prefixes_to_filter:
                        pattern = rf'^{re.escape(prefix)}.*?(\n\n|\Z)'
                        # 使用 re.DOTALL (让.匹配换行符) 和 re.MULTILINE (让^匹配每行开头)
                        new_text = re.sub(pattern, '', new_text, flags=re.DOTALL | re.MULTILINE)
                
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
