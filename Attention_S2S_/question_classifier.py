# -*- coding: utf-8 -*-
import ahocorasick
import os
class QuestionClassifier:
    def __init__(self):
        # cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        #　特征词路径
        # self.star_path = os.path.join(cur_dir, 'dict/star.txt')
        self.star_wds = [i.strip() for i in open('dict/star.conv',encoding='utf-8') if i.strip()]
        self.region_words = set(self.star_wds)
        #构造actree
        self.region_tree = self.build_actree(list(self.region_words))
        # 构建词典
        self.wdtype_dict = self.build_wdtype_dict()
        self.star_qws = ['运势', '运气', '运']

    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    '''问句过滤'''

    def check_medical(self, question):
        region_wds = []
        for i in self.region_tree.iter(question):  # i 的形状(index, (index, word))
            wd = i[1][1]  # word
            region_wds.append(wd)
            '''注释部分暂时不用, 多知识时再添加'''
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)
        final_wds = [i for i in region_wds if i not in stop_wds]
        final_dict = {i: self.wdtype_dict.get(i) for i in final_wds}

        return final_dict
        # return region_wds
    '''答案词典们, 以后考虑使用neo4j来代替'''
    star_fate_dict = {
        '白羊座':'白羊座的人会有深刻的想法和关键的改变，但是你们所有人都在期待一个难忘的2020年的开始。这仅仅是个开始——接受建议，对自己宽容一点',
        '金牛座':'一月不可预测的天王星在金牛座，预示着在2020年新的想法和内在的不安.如果你的工作需要谈话、写作、教学或说服他人，那么这些行星会支持你。只要记住，没有什么是容易的，所取得成就都是持久坚持的结果。',
        '双子座':'对双子座来说，处理任何与家庭、项目、计划有关的事情都不是一件容易的事情——他们要求苛刻，工作缓慢，需要耐心。这个月你不能突破界限或象征性的封印，但你可以为自己和你爱的人建立更安全的东西。',
        '巨蟹座':'巨蟹座1月的月食会激发你最深的情感和激动的精神感觉。你可以调到任何你想要的，如果你正在学习，探索新的想法，或计划一次旅行，那么你会受到启发。',
        '狮子座':'2020年对于狮子座来说是个人工作快速发展，事业腾飞的一年。他们在年初就能够凭借着土星与冥王星相合落于摩羯宫，从而迎来更为稳定的事业运。',
        '处女座':'对于处女座来说,有时创造力需要耐心。你已经播下了种子，现在你必须等待，直到你看到新芽。所以，敞开你的心扉，接受各种可能性——尤其是那些与旅行、教学、学习或外国人有关的可能性。慢慢来，命里有时终须有。',
        '天秤座':'对于天秤座来说，2020年是一个变化较大的一年，在这一年里他们的各项运势都不是很稳定，尤其是在工作中需要面临很多选择。所以在这一年里天秤座们必须要做好心理准备，当问题了来临之后可以冷静对待。',
        '天蝎座':'对于天蝎座来说,你所写的、所说的、所宣传的都会对一月份产生真正的影响。你与他人的联系是至关重要的，所以一定要保持联系，或者出去走走——即使你真的不想这样。这里也有一条双行道——你将与你生活中的其他人、邻居和更远的地方打交道——可能比平时更多。',
        '射手座':'射手座今年会热衷于推动事情向前发展，或者让其他人加入到激动人心的计划或项目中来。如果你把精力用在关心和关注上，你就能以积极的方式开始2020年。但是你也要实际一点，不要因为别人花了时间或者你梦想的结果迟迟没有实现而失去它。',
        '魔羯座':'2020年伊始，你是真正的宇宙摩羯座——海山羊。主要是关于你，也可能是你的伴侣，工作伙伴，以及友谊。这对你来说可能是一个非凡的时刻，但它也带来了很多责任——对你们中的许多人来说——还有一些非常重要的决定。',
        '水瓶座':'一月份开始，水瓶座有很多事情要考虑。很多事情似乎都超出了你的控制范围，所以不要为那些烦人的新年计划感到压力。与此同时，大步前进，保持灵活。2020年的春天对于很多水瓶座的人来说是一个改变游戏规则的时刻——你的新年即将从那时开始。',
        '双鱼座':'双鱼座很难应对2020年中各项运势的变化，在这一年里土星与冥王星相合，而且还会在年初落入到他们的第十一宫当中，这会给双鱼座的工作、生活带来极大地改变。尤其是在人际交往方面他们会面临人缘“干涸”，身边能够信任的人并不多，这对于双鱼座的影响还是相当大的。'
    }
    star_dict = {
        '白羊座':'白羊座有一种让人看见就觉得开心的感觉',
        '双子座':'双子座喜欢追求新鲜感，有点儿小聪明，就是耐心不够',
        '金牛座':'金牛座很保守，喜欢稳定，一旦有什么变动就会觉得心里不踏实',
        '巨蟹座':'巨蟹座的情绪容易敏感，也缺乏安全感，容易对一件事情上心',
        '狮子座':'狮子座有着宏伟的理想，总想靠自己的努力成为人上人',
        '处女座':'处女座虽然常常被黑，但你还是依然坚持追求自己的完美主义',
        '天秤座':'天秤座常常追求平等、和谐，擅于察言观色，交际能力很强',
        '天蝎座':'天蝎座精力旺盛、占有欲极强，对于生活很有目标',
        '射手座':'射手座崇尚自由，勇敢、果断、独立，身上有一股勇往直前的劲儿',
        '魔羯座':'摩羯座是十二星座中最有耐心，为事最小心、也是最善良的星座',
        '水瓶座':'水瓶座的人很聪明，他们最大的特点是创新，追求独一无二的生活',
        '双鱼座':'双鱼座是十二宫最后一个星座，他集合了所有星座的优缺点于一身'
    }
    star_fortunes_dict = {
        '白羊座': '白羊座财运方面运势普通，投资理财方面比较谨慎、小心，不熟悉的项目是不会考虑入手的',
        '双子座': '双子座财运方面运势平平，投资理财方面比较随缘，没什么特别大的发财野心',
        '金牛座': '金牛座财运方面运势一般，投资理财方面能够走出某些误区，找到更合适的项目了',
        '狮子座': '狮子座财运方面运势平平，投资理财方面别高估了自己的能力，多请教专业人士为宜',
        '处女座': '处女座财运方面运势一般，投资理财方面你也许会通过一系列的筛选，找到适合自己的项目',
        '天秤座': '天秤座财运方面运势还好，投资理财方面可能会有人给你提供一些机会',
        '天蝎座': '天蝎座财运方面运势普通，投资理财方面不宜操之过急，要小心误入陷阱造成损失',
        '射手座': '射手座财运方面运势普通，投资理财方面可能会投入多、收益少',
        '魔羯座': '摩羯座财运方面运势一般，投资理财方面好的项目会有不少人都盯着，想要入手不是件简单的事情',
        '水瓶座': '水瓶座财运方面运势还好，投资理财方面会有些较大的布局改变，收益能获得不少',
        '双鱼座': '双鱼座财运方面运势一般，投资理财方面胆子放大一点，做决定别犹豫'
    }
    star_today = {
        '白羊座': '',
        '双子座': '',
        '金牛座': '',
        '巨蟹座': '',
        '狮子座': '',
        '处女座': '',
        '天秤座': '',
        '天蝎座': '',
        '射手座': '',
        '魔羯座': '',
        '水瓶座': '',
        '双鱼座': ''
    }
    star_tommorow = {
        '白羊座': '',
        '双子座': '',
        '金牛座': '',
        '巨蟹座': '',
        '狮子座': '',
        '处女座': '',
        '天秤座': '',
        '天蝎座': '',
        '射手座': '',
        '魔羯座': '',
        '水瓶座': '',
        '双鱼座': ''
    }
    star_thisweek = {
        '白羊座': '',
        '双子座': '',
        '金牛座': '',
        '巨蟹座': '',
        '狮子座': '',
        '处女座': '',
        '天秤座': '',
        '天蝎座': '',
        '射手座': '',
        '魔羯座': '',
        '水瓶座': '',
        '双鱼座': ''
    }
    star_nextweek = {
        '白羊座': '',
        '双子座': '',
        '金牛座': '',
        '巨蟹座': '',
        '狮子座': '',
        '处女座': '',
        '天秤座': '',
        '天蝎座': '',
        '射手座': '',
        '魔羯座': '',
        '水瓶座': '',
        '双鱼座': ''
    }



    '''构造词对应的类型'''

    def build_wdtype_dict(self):
        wd_dict = dict()
        for wd in self.region_words:
            wd_dict[wd] = []
            if wd in self.star_wds:
                wd_dict[wd].append('star')
        return wd_dict

    '''基于特征词进行分类'''

    def check_words(self, wds, sent):
        for wd in wds:
            if wd in sent:
                return True
        return False

    '''主函数'''
    def classify(self, question):
        s2s = False
        data = {}
        medical_dict = self.check_medical(question)
        if not medical_dict:
            return False
        data['args'] = medical_dict
        #收集问句当中所涉及到的实体类型
        types = []
        star_n = 'no'
        for type_ in medical_dict.values():
            types += type_
        question_types = []
        for k,v in medical_dict.items():
            if v == ['star']:
                star_n = k
                break
        if self.check_words(self.star_wds, question) and self.check_words(['财运','财'], question) and ('star' in types):
            question_type = 'star_fortunes'
            question_types.append(question_type)
            return self.star_fortunes_dict[star_n]
        if self.check_words(self.star_wds, question) and self.check_words(self.star_qws, question) and ('star' in types):
            question_type = 'star_fate'
            question_types.append(question_type)
            return self.star_fate_dict[star_n]
        if self.check_words(self.star_wds, question) and ('star' in types):
            question_type = 'star'
            question_types.append(question_type)
            return self.star_dict[star_n]


# if __name__ == '__main__':
    # chack_model = QuestionClassifier()
    # text = str(input('星座测试:'))
    # # text = '本周双子座的运势处女座怎么样'
    # topic = 'None'
    # question_type ='None'
    # list = chack_model.check_medical(text)
    # print(list)
    # if len(list)==0:
    #     print('返回生成回答')
    # for wd in list:
    #     if wd in chack_model.star_dict:
    #         question_type = 'star'
    #         for wd in list:
    #             if wd in chack_model.star_qws:
    #                 question_type = 'star_fate'
    #
    # for wd in list:
    #     if wd in chack_model.star_dict:
    #         if question_type == 'star':
    #             print(chack_model.star_dict[wd])
    #             break
    #         elif question_type == 'star_fate':
    #             print(chack_model.star_fate_dict[wd])
    #             break

    # for wd in list:
    #     if wd in chack_model.star_dict:
    #         topic= 'star'
    #         for wd in list:
    #             if wd in chack_model.star_qws:
    #                 question_type = 'fate'
    #         break
    # if topic == 'star':
    #     if question_type == 'fate':
    #         print(chack_model.star_fate_dict[wd])
    #     elif question_type == 'None':
    #         print(chack_model.)




