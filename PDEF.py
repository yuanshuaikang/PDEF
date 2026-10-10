import math
from math import sqrt
import random
import collections
import time
# from memory_profiler import profile

f = open(r"D:\PSO-MUCP 代码\IDEA co-location\数据文档\Toronto_POI 16f.csv", "r",
         encoding="UTF-8")  # AA.text BB.text CC.text
Instance = []
for line in f:
    temp_2 = []
    temp = line.strip().split(",")
    if temp != [''] and temp != ['Feature', 'Instance', 'LocX', 'LocY', 'Checkin']:
        # print(temp)
        s = temp[0] + temp[1]
        temp_2.append(s)
        temp_2.append(float(temp[2]))
        temp_2.append(float(temp[3]))
        Instance.append(temp_2)
        # print(Instance)
f.close()

Utility = {
    'A': 2, 'B': -10, 'C': 8, 'D': 4, 'E': 1, 'F': 4, 'G': -5, 'H': 3, 'I': 13, 'J': 3,
    'K': 5, 'L': -14, 'M': 8, 'N': 2, 'O': -6, 'P': 4
}

Min_utility = 50
D = 40 # 距离阈值越大生成得邻近关系越多

start_time = time.time()


#  计算出每个特征的总效用然后将特征按照总效用从大到小排列
def Compute_utility(Utility, instance):
    utility_dict = {}
    feature_instance = {}
    for elem in Utility.keys():
        if elem not in feature_instance.keys():
            feature_instance[elem] = 0
        number_instance = 0
        for i in instance:
            if i[0][0] == elem:
                number_instance += 1
        utility_dict[elem] = number_instance * Utility[elem]
        feature_instance[elem] = number_instance
    all_utility = 0
    for elem in utility_dict.keys():
        all_utility += utility_dict[elem]
    return all_utility, feature_instance


#  计算出所有的实例邻近关系
def computed_neigh(instance_1, instance_2, d):
    x = instance_1[1] - instance_2[1]
    y = instance_1[2] - instance_2[2]
    distance_12 = sqrt(x ** 2 + y ** 2)
    if distance_12 <= d:
        return True
    else:
        return False


def grid_method(i, d):
    """
    采用网格法计算每一个实例的邻近结点，每一个实例只用检查本身所在网格以及与它相邻的八个方向的网格
    :param i: 实例集
    :param d: 网格变成（距离阈值）
    :return: Ns，PNs，SNs
    """
    # 找到整个网格的范围，对网格进行划分，并将实例分配进对应的网格
    x_min = min(x[1] for x in i)
    y_min = min(x[2] for x in i)
    hash_grid = {}
    for elem in i:
        x_order = math.ceil((elem[1] - x_min) / d)
        y_order = math.ceil((elem[2] - y_min) / d)
        if x_order == 0:
            x_order += 1
        if y_order == 0:
            y_order += 1
        hash_grid.setdefault((x_order, y_order), []).append(elem)

    # 根据划分的网格计算每个实例的邻近关系
    Ns = {}
    computed_neigh = lambda x, y, d: (x[1] - y[1]) ** 2 + (x[2] - y[2]) ** 2 <= d ** 2
    for elem_hash, grid_instances in hash_grid.items():
        for elem_list in grid_instances:
            Ns.setdefault(elem_list[0], [])
            for x in grid_instances:
                if x[0][0] != elem_list[0][0] and computed_neigh(x, elem_list, d):
                    Ns[elem_list[0]].append(x[0])

            # 计算相邻的八个方向
            for delta_x in range(-1, 2):
                for delta_y in range(-1, 2):
                    if delta_x == delta_y == 0:
                        continue
                    adjacent_grid = (elem_hash[0] + delta_x, elem_hash[1] + delta_y)
                    if adjacent_grid in hash_grid:
                        for elem_xy in hash_grid[adjacent_grid]:
                            if elem_xy[0][0] != elem_list[0][0] and computed_neigh(elem_xy, elem_list, d):
                                Ns[elem_list[0]].append(elem_xy[0])
    return Ns


#  计算粗略上界并剪枝
def Prune_one(nis, utility, min_utility, ALL):
    extend_utility = {}  # 存放每个特征的扩展效用
    have_traversal = {}  # 存放该实例是否已经被计算到扩展效用中

    for nis_ket in nis.keys():
        if nis_ket[0] not in have_traversal.keys():
            have_traversal[nis_ket[0]] = []  # 初始化
            extend_utility[nis_ket[0]] = 0

        have_traversal[nis_ket[0]] = list(set(have_traversal[nis_ket[0]]) | set(nis[nis_ket]))
        have_traversal[nis_ket[0]].append(nis_ket)

    ins_number = {}
    for item in have_traversal.keys():
        ins_number[item] = 0
        for item_elem in have_traversal[item]:
            # print(utility)
            # print(item_elem)
            ins_number[item] += 1
            extend_utility[item] += utility[item_elem[0]]

    #  删除上界小于min的特征
    delete = []
    for up_key in extend_utility.keys():
        if extend_utility[up_key] < min_utility:
            delete.append(up_key)
    return delete, ins_number


# 计算初始概率
def initial_probability(feature_instance, utility, instance_neighbor, delete):
    #  记录所有的特征的初始生成概率
    probability = {}
    #  先得到参数
    beita = 0.2  # 控制实例的参数111111111111111111111111111111111111111111111111
    #  计算参数C
    temp = {}
    averge = 0
    count = 0  # count=0是因为模式全部被删除了
    for feature in utility.keys():
        if feature in delete:
            continue

        # 如果该特征在数据集中没有实例，直接跳过
        if feature_instance.get(feature, 0) == 0:
            continue

        # 如果该特征没有邻近统计，也直接跳过
        if feature not in instance_neighbor:
            continue

        # 负效用特征不能直接 log(utility + 1)，否则 B、G、L、O 这类负数会出问题
        if utility[feature] <= 0:
            continue

        log_neighbor_x = math.log(instance_neighbor[feature] + 1, 2)
        log_utility_x = math.log(utility[feature] + 1, 2)
        log_instance_x = math.log(feature_instance[feature] ** beita + 1, 2)

        temp[feature] = log_neighbor_x * log_utility_x * log_instance_x
        averge += temp[feature]
        count += 1
    if count == 0:
        return {}

    C = averge / count
    # print(C)
    aerfa = 0.025  # 参数aerfa3333333333333333333333333333333333333333333333333
    for key in temp.keys():
        probability[key] = 1 / (1 + math.e ** (-aerfa * (temp[key] - C)))
    return probability


def structure_tree(i, can_key, nis, temp_clique, key, inter, A):
    if len(inter) == 0:
        return
    if i == len(can_key) and temp_clique not in A:
        A.append(temp_clique)
        return

    for elem in inter:
        if elem[0] == can_key[i]:
            new_temp_clique = temp_clique + [elem]
            new_inter = sorted(list(set(nis[elem]) & set(inter)))
            structure_tree(i + 1, can_key, nis, new_temp_clique, key, new_inter, A)
            if len(new_temp_clique) + 1 == len(can_key):
                A.append(new_temp_clique)
    return


def Enum_Cliques(nis, can_key):
    # 构建一颗树
    tree = {}
    for key in nis.keys():
        i = 1  # 记录现在是树的第几层
        A = []
        if key[0] == can_key[i - 1]:
            tree[key] = []  # 生成头节点
            for elem in nis[key]:  # 遍历头节点的邻近关系找到对应特征的实例 进入a1
                if elem[0] == can_key[i]:
                    temp_clique = [elem]  # 存储暂时团
                    if len(can_key) > i + 1:
                        inter = sorted(list(set(nis[elem]) & set(nis[key])))
                        # print(key, elem, inter)
                        structure_tree(i + 1, can_key, nis, temp_clique, key, inter, A)
                    else:
                        tree[key].append(temp_clique)
            # print(A,'AAAAAAAAAAAA')
            if len(A) != 0:
                for elem in A:
                    tree[key].append(elem)
            if len(tree[key]) == 0:
                del tree[key]
            # print(tree)
    return tree


#  计算当前模式的效用
def compute_utility(tree, utility, can_pattern, all, contribution):
    feature_number = {}

    for feature in can_pattern:
        feature_number[feature] = []
    for key in tree.keys():
        feature_number[key[0]].append(key)
        for elem in tree[key]:
            for elem_1 in elem:
                if elem_1 not in feature_number[elem_1[0]]:
                    feature_number[elem_1[0]].append(elem_1)

    str = ""  # 当前模式
    for feature in can_pattern:
        str += feature
    contribution[str] = {}
    pattern_utility = 0
    # print(feature_number)
    for key in feature_number.keys():
        pattern_utility += len(feature_number[key]) * utility[key]
        contribution[str][key] = (len(feature_number[key]) * utility[key])
    # print(pattern_utility)
    return pattern_utility


#  计算每个特征的贡献率
def compute_contribution(contribution, excellent_s, o):
    #  不需要每个特征都改变概率,只将出现的精英样本更新概率
    #  首先获得所有需要更新的特征
    feature_update_pr = {}
    for sample in excellent_s:
        for al in sample:
            if al not in feature_update_pr.keys():
                feature_update_pr[al] = 0
    # print(feature_update_pr)

    #  按照顺序依次计算每个特征的概率
    for feature in feature_update_pr.keys():
        all_appear_utility = 0  # 出现该特征的总效用
        feature_contribution = 0  # 该特征的贡献效用
        count = 0  # 记录这个出现该特征的模式的个数
        # print(feature)
        # print('精英样本', excellent_s)

        for sample in excellent_s:
            if feature in sample:
                for elem in contribution[sample]:
                    all_appear_utility += contribution[sample][elem]
                    if elem == feature:
                        count += 1
                        feature_contribution += contribution[sample][feature]
        # all_appera_utility为0的话说明数据集太稀疏了，没有行实例可以满足当前的候选模式，即使取前百分之30精英样本来更新也是为0
        if all_appear_utility != 0:
            feature_update_pr[feature] = ((o + ((1 - o) * feature_contribution / all_appear_utility)) * count) / len(
                excellent_s)
        # print(feature_contribution, all_appear_utility)
    # print(feature_update_pr)
    return feature_update_pr


#  主函数
def CE(init_probability, delete, all, min_utility, nis, utility):
    gap = 5  # 设定迭代的窗口大小
    t = 300  # 设定迭代次数 5555555555555555555555555555555555
    accept = 0.3  # 可接受的下降因子 66666666666666666666666666666666
    Satisfy_constraints = []  # 记录满足约束的模式数量
    current_t = 1  # 当前迭代
    variation = 0  # 已经变异的次数
    have_variation = []  # 已经变异的特征集合
    r = 0.9  # 历史迭代的影响权重
    z = 100  # 样本空间大小减小速率 越大减少速度越慢
    N0 = 500
    current_N = 500  # 生成初始N0个样本 4444444444444444444444444444444444444444444444444444444
    high_utility_pattern = {}
    have_exam = []  # 记录已经检查过的模式
    O = 0.9  # 控制基本贡献率 88888888888888888888888888888888888888888888888888888888888888888 o越大贡献率考虑的越少
    ture = []

    feature_list = list(init_probability.keys())  # 所有特征的集合
    list2 = [item for item in feature_list if item not in delete]  # 没有被删除的特征集合
    current_p = {}  # 没有被删出的特征的概率集合
    for elem in list2:
        current_p[elem] = init_probability[elem]

    while current_t <= t:
        # print(current_p, "迭代的概率")
        # 首先需要检查是否需要变异
        if variation <= gap:
            if current_t > gap + 1:
                count = 0
                for i in range(2, gap + 2):
                    count += Satisfy_constraints[current_t - i - 1]
                Change = accept * count / gap
                # print(Change)
                if Satisfy_constraints[current_t - 2] <= Change:  # 判断是否需要变异的条件
                    print('本次循环概率变异了11111111111111111111111')
                    # print(current_p)

                    # 找到所有概率小于 0.5 且未变异过的特征
                    low_prob_features = [feature for feature in current_p.keys()
                                         if current_p[feature] < 0.5 and feature not in have_variation]

                    # 如果存在满足条件的特征，则随机选择一个并设置其概率为 0.5
                    if low_prob_features:
                        selected_feature = random.choice(low_prob_features)
                        # print(selected_feature)
                        current_p[selected_feature] = 0.5
                        have_variation.append(selected_feature)
                    variation += 1
                else:
                    variation = 0

        # 检查是否需要减少样本空间
        if variation >= gap:
            # 首先算出历史迭代满足约束的平均数
            aver = 0
            max = 0
            for i in range(1, gap + 1):
                aver += (r ** i) * Satisfy_constraints[current_t - i - 1]
                if Satisfy_constraints[current_t - i - 1] > max:
                    max = Satisfy_constraints[current_t - i - 1]
            if max == 0:
                current_N = int(current_N * math.exp(-z))
            else:
                current_N = int(current_N * math.exp(-z * aver / max))
            # print(current_N, math.exp(-z * aver / max), "样本空间")

        # 根据更新过的概率和样本空间生成样本
        can_list = []  # 存放生成的样本
        i = 0
        while i < current_N:
            selected_letters = []

            # 按顺序依次选择字母  这里有问题!!!!!!
            for letter, probability in current_p.items():
                if random.random() < probability:  # 根据概率决定是否选择
                    selected_letters.append(letter)
            i += 1
            if len(selected_letters) > 1:
                can_list.append(selected_letters)
        # print(len(can_list))  # 生成的样本

        #  检查候选模式
        number = 0  # 记录当前迭代满足约束的个数
        exam_num = 0
        pattern_utility = {}  # 记录当前样本的情况
        Contribution = {}  # 记录当前迭代每个模式的贡献率
        for elem in can_list:
            str = ""  # 当前模式
            if elem not in have_exam:
                exam_num += 1
                TREE = Enum_Cliques(nis, elem)  # 找到行实例
                UR = compute_utility(TREE, utility, elem, all, Contribution)  # 计算模式的效用率
                for feature in elem:
                    str += feature
                pattern_utility[str] = UR  # 记录模式的效用率
                high_utility_pattern[str] = {}
                if UR >= min_utility:
                    ture.append(str)
                    high_utility_pattern[str] = Contribution[str]
                    number += 1
                have_exam.append(elem)
        Satisfy_constraints.append(number)
        # print(Contribution)
        # print(high_utility_pattern)
        # print(pattern_utility)
        print(exam_num, '本次循环被检查的模式个数222222222222')
        print("第", current_t, '次迭代发现：', len(ture), "高效用模式的个数")

        #  现在还差最后的概率更新 如果前gap次迭代使用前百分值p的精英样本更新概率 因为前几次迭代高效用模式可能不够作为概率样本更新的条件
        p = 0.3  # 前gap次迭代取前百分之p的精英样本更新概率7777777777777777777777777777777777777777777
        if len(pattern_utility) != 0:  # 只有不为空的时候才更新概率 将模式从小到大排列
            if current_t <= gap:
                sorted_pattern_utility = dict(
                    collections.OrderedDict(sorted(pattern_utility.items(), key=lambda x: x[1], reverse=True)))
                elit = []
                for key_pattern in sorted_pattern_utility.keys():
                    if sorted_pattern_utility[key_pattern] >= Min_utility:
                        elit.append(key_pattern)

                pattern_num = int(p * len(elit))
                excellent_sample = []
                i = 0
                for key_patterns in excellent_sample:
                    excellent_sample.append(key_patterns)
                    i += 1
                    if i == pattern_num:
                        break
                #  有了精英样本和精英样本每个特征对应的贡献,就可以计算它的贡献率了
                Contributed_ratio = compute_contribution(Contribution, excellent_sample, O)
                # print(Contributed_ratio)
            else:
                # print('xxxxxxxxxxxxxxxxxxxxxxxx')
                Contributed_ratio = compute_contribution(high_utility_pattern, ture, O)
            for k_p in Contributed_ratio.keys():  # 更新概率
                if current_t <= gap and current_p[k_p] != 0:
                    Contributed_ratio[k_p] = Contributed_ratio[k_p]
                if current_t > gap:
                    current_p[k_p] = Contributed_ratio[k_p]
        current_t += 1

        print("样本空间大小", current_N)
        #  还缺少提前停止的条件停止的条件
        if current_N <= N0 * 0.1:  # 如果样本空间小于初始样本空间的0.1那就直接输出
            return ture

        print(Satisfy_constraints)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"程序运行时间: {elapsed_time} 秒")
    return ture


# @profile
def my_func():
    ALL_utility, Feature_instance = Compute_utility(Utility, Instance)
    # print(ALL_utility)  # 数据集的总效用
    # print(Feature_instance)  # 每个特征的数量
    NIS = grid_method(Instance, D)
    # print(NIS)  # 邻近实例集
    Delete, Instance_neighbor = Prune_one(NIS, Utility, Min_utility, ALL_utility)
    #  Delete是删除的特征集合  Instance_neighbor是每个特征相邻实例的个数
    # print(Delete, Instance_neighbor)
    Probability = initial_probability(Feature_instance, Utility, Instance_neighbor, Delete)
    print(Probability)
    ture_pattern = CE(Probability, Delete, ALL_utility, Min_utility, NIS, Utility)
    print("输出高效用模式:", len(ture_pattern))

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"程序运行时间: {elapsed_time} 秒")


if __name__ == "__main__":
    my_func()
