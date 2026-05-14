import asyncio

import click


@click.command()
def web():
    """启动Web界面"""
    try:
        import gradio as gr
    except ImportError:
        print("需要安装 gradio: pip install gradio")
        return

    from src.core.personality import Personality
    from src.core.chat import ChatEngine
    from src.ai.llm import LLMClient
    from src.core.init import ensure_db
    from src.core.recommender import Recommender

    def _run_async(coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    _run_async(ensure_db())
    personality = Personality()
    llm = LLMClient()
    engine = ChatEngine(personality, llm)
    recommender = Recommender(personality)

    def chat_fn(message, history):
        reply = _run_async(engine.chat(message))
        return reply

    def recommend_fn(mood, scene):
        if mood:
            songs = _run_async(recommender.recommend_by_mood(mood, 5))
            title = f"心情「{mood}」推荐"
        elif scene:
            songs = _run_async(recommender.recommend_by_scene(scene, 5))
            title = f"场景「{scene}」推荐"
        else:
            songs = _run_async(recommender.recommend_from_liked(5))
            title = "根据收藏推荐"
        result = f"## {personality.name} 的 {title}\n\n"
        for s in songs:
            label = f"**{s['name']}**"
            if s.get("artist"):
                label += f" - {s['artist']}"
            result += f"- {label}: {s['reason']}\n"
        return result if songs else "还没有数据，请先登录网易云同步"

    def daily_fn():
        result = _run_async(recommender.get_daily_recommendation())
        text = f"## 📅 {personality.name} 的每日推荐\n\n"
        text += f"心情: {result['mood']} | 精力: {result['energy']}\n\n"
        for s in result.get("songs", []):
            label = f"**{s['name']}**"
            if s.get("artist"):
                label += f" - {s['artist']}"
            text += f"- {label}: {s['reason']}\n"
        return text

    with gr.Blocks(title="音伴", theme=gr.themes.Soft()) as app:
        gr.Markdown(f"# 🎵 音伴 — {personality.name}")
        gr.Markdown(f"*{personality.bio}*")

        with gr.Tab("聊天"):
            gr.ChatInterface(chat_fn, title=f"和{personality.name}聊天")

        with gr.Tab("推荐"):
            with gr.Row():
                mood_input = gr.Dropdown(
                    ["开心", "平静", "伤感", "烦躁", "慵懒", "热情"],
                    label="按心情推荐",
                )
                scene_input = gr.Dropdown(
                    ["深夜", "学习", "跑步", "通勤", "工作"],
                    label="按场景推荐",
                )
            recommend_btn = gr.Button("推荐")
            recommend_output = gr.Markdown()
            recommend_btn.click(recommend_fn, [mood_input, scene_input], recommend_output)

        with gr.Tab("每日推荐"):
            daily_btn = gr.Button("获取今日推荐")
            daily_output = gr.Markdown()
            daily_btn.click(daily_fn, None, daily_output)

    app.launch()
