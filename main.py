from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.message_components import Plain, BaseMessageComponent
from astrbot.api.star import Context, Star, register
import re

@register("astrbot_plugin_thinkTags", "长安某", "过滤think/thinking/disclaimer标签", "1.2.0")
class FilterThinkTagsPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.on_decorating_result()
    async def on_decorating_result(self, event: AstrMessageEvent):
        result = event.get_result()
        chain = result.chain

        new_chain = []
        for component in chain:
            if isinstance(component, Plain):
                # 匹配 <think>...</think>、<thinking>...</thinking> 或 <disclaimer>...</disclaimer> 及其包裹的内容
                new_text = re.sub(
                    r'<(think|thinking|disclaimer)>.*?</\1>\s*',
                    '',
                    component.text,
                    flags=re.DOTALL
                )
                # 过滤无标签的纯文本 "Thinking: ..."
                new_text = re.sub(r'Thinking:\s*.*?(\n|$)', '', new_text, flags=re.DOTALL)
                new_chain.append(Plain(new_text.strip()))  # 移除首尾空格
            else:
                new_chain.append(component)

        result.chain = new_chain
