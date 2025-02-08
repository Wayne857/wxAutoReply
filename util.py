import yaml
import os
import time
from langchain.chains.llm import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_models import ChatTongyi
from langchain_community.llms.tongyi import Tongyi
from langchain_core.prompts import PromptTemplate
from wxauto import WeChat


# 从yaml获取配置信息
def get_config(cfg_path: str) -> dict:
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
        print(cfg)
    return cfg


def getChain():
    cfgs = get_config("config.yaml")
    os.environ["DASHSCOPE_API_KEY"] = cfgs["API"]["api_Key"]
    llm = ChatTongyi(model=cfgs["API"]["model_name"])
    template = f"""{cfgs["template"]}"""
    prompt = PromptTemplate(
        input_variables=["chat_history", "human_input"], template=template
    )
    memory = ConversationBufferMemory(memory_key="chat_history")
    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
        memory=memory,
    )
    return llm_chain


def messageProcess(llm_chain):
    cfgs = get_config("config.yaml")
    # 获取微信窗口对象
    wx = WeChat()
    # 设置监听列表
    listen_list = cfgs["nameList"]
    # 循环添加监听对象
    for i in listen_list:
        wx.AddListenChat(who=i, savepic=True)

    # 持续监听消息，并且收到消息后回复“收到”
    wait = 1  # 设置1秒查看一次是否有新消息
    while True:
        msgs = wx.GetListenMessage()
        print("摆烂中...")
        for chat in msgs:
            who = chat.who  # 获取聊天窗口名（人或群名）
            one_msgs = msgs.get(chat)  # 获取消息内容
            # 回复收到
            for msg in one_msgs:
                msgtype = msg.type  # 获取消息类型
                content = msg.content  # 获取消息内容，字符串类型的消息内容
                print(f'【{who}】：{content}')

                # 如果是好友发来的消息（即非系统消息等），则回复收到
                if msgtype == 'friend':
                    question = content
                    result = llm_chain.predict(human_input=question)
                    chat.SendMsg(result)  # 回复收到
                    print(f'------->回复【{content}】：{result}')
        time.sleep(wait)


def main():
    llm_chain = getChain()
    messageProcess(llm_chain)

