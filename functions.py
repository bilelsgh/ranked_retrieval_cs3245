import os


def clean():
        for docID in os.listdir("index/dict"):
                file = "index/dict/{}".format(docID)
                os.remove(file)

        for docID in os.listdir("index/post"):
                file = "index/post/{}".format(docID)
                os.remove(file)

if __name__ == "__main__":
        clean()