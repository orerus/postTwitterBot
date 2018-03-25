from twitterAPIKey import TwitterAPIKey
import sys
sys.path.append('/home/ec2-user/workspace/work')

class TwitterAPIManager:

    # 作成したAPIキーをTwitterAPIKeyクラスにセットし、APIKeysリストに詰めておく
    # key１つで15分間に300リクエスト、すなわち毎分20リクエストまで。
    # よってキーの数 * 20アカウントが取得制限目安。    
    key1 = TwitterAPIKey(
        'hogehoge1',
        'fugafuga',
        '00000000-hogefuga',
        'fugahoge')
    key2 = TwitterAPIKey(
        'hogehoge2',
        'fugafuga',
        '00000000-hogefuga',
        'fugahoge')
    key3 = TwitterAPIKey(
        'hogehoge3',
        'fugafuga',
        '00000000-hogefuga',
        'fugahoge')
    key4 = TwitterAPIKey(
        'hogehoge4',
        'fugafuga',
        '00000000-hogefuga',
        'fugahoge')
    key5 = TwitterAPIKey(
        'hogehoge5',
        'fugafuga',
        '00000000-hogefuga',
        'fugahoge')

    APIKeys = [key1, key2, key3, key4, key5]
    currentIndex = -1
    
    def nextKey(self):
        self.currentIndex += 1
        if self.currentIndex >= len(self.APIKeys):
            self.currentIndex = 0
        return self.APIKeys[self.currentIndex]
