import cv2
import os
from PIL import Image
from github import Github
import base64
from zhipuai import ZhipuAI

# 设置您的 Google API密钥和Qiniu访问令牌
GITHUB_TOKEN = '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'
REPO_NAME = 'ebbdYan/extract_video'
BRANCH_NAME = 'main'  # 或者您想要上传到的分支名称

def upload_to_github(file_path, github_path):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    with open(file_path, 'rb') as file:
        content = file.read()
    try:
        contents = repo.get_contents(github_path, ref=BRANCH_NAME)
        repo.update_file(contents.path, f"Update{github_path}", content, contents.sha, branch=BRANCH_NAME)
    except:
        repo.create_file(github_path, f"Create{github_path}", content, branch=BRANCH_NAME)
    return f"https://raw.githubusercontent.com/{REPO_NAME}/{BRANCH_NAME}/{github_path}"

def describe_png(image_url):
    client = ZhipuAI(api_key="cf2ef25ab1f9a7b366187c7686204798.CnPd0MW2IKqrTKUh")  # 填写您自己的 APIKey
    response = client.chat.completions.create(
        model="glm-4v",
        messages=[{"role": "user", "content": [{"type": "text", "text": "请描述这个图片"}, {"type": "image_url", "image_url": {"url": image_url}}]}],
        top_p=0.7,
        temperature=0.95,
        max_tokens=1024,
        stream=False
    )
    res = response.choices[0].message.content
    print(res)
    return res

def extract_frames_and_analyze(video_path, output_folder, interval=4):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * interval)
    frame_count = 0
    extracted_count = 0
    results = []

    while True:
        success, frame = video.read()
        if not success:
            break

        if frame_count % frame_interval == 0:
            output_path = os.path.join(output_folder, f"frame_{extracted_count:04d}.jpg")
            cv2.imwrite(output_path, frame)

            github_path = f"video_frames/frame_{extracted_count:04d}.jpg"
            qiniu_url = upload_to_github(output_path, github_path)
            print(qiniu_url)

            # 使用分析图片
            response = describe_png(qiniu_url)

            # 保存分析结果
            analysis_path = os.path.join(output_folder, f"analysis_{extracted_count:04d}.txt")
            with open(analysis_path, 'w', encoding='utf-8') as f:
                f.write(f"Qiniu URL: {qiniu_url}\n\n")
                f.write(response)
            # 将结果添加到列表中
            results.append({
                'frame': extracted_count,
                'qiniu_url': qiniu_url,
                'analysis': response
            })

            print(f"已分析并上传第{extracted_count}帧")
            extracted_count += 1
            frame_count += 1

            video.release()
            print(f"总共提取、分析并上传了{extracted_count}帧图片")
            return results
        
def main():
    # 使用示例
    video_path = "./调料罐.mp4"  # 替换为你的视频文件路径
    output_folder = "output_frames_and_analysis"  # 输出文件夹名称
    results = extract_frames_and_analyze(video_path, output_folder, 20)

    # 打印结果
    for result in results:
        print(f"Frame {result['frame']}:")
        print(f"Qiniu URL: {result['qiniu_url']}")
        print(f"Analysis: {result['analysis']}")
        print("-" * 50)

if __name__ == '__main__':
    main()