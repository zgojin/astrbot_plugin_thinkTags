from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.message_components import Plain, BaseMessageComponent
from astrbot.api.star import Context, Star, register
import re

@register("filter_think_tags", "长安某", "简单的过滤think", "1.0.0")
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
                # 如果是纯文本消息段，过滤掉 <think> 和 </think> 及其包裹的内容，并移除前面的空格
                new_text = re.sub(r'<think>.*?</think>\s*', '', component.text, flags=re.DOTALL)
                new_chain.append(Plain(new_text))
            else:
                # 其他类型的消息段直接添加到新链中
                new_chain.append(component)

        result.chain = new_chain
