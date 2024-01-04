from ... import context as c

def create_prompt(name, model, weight, user_prompt, negative_prompt, pids):
    prompts = []
    if pids:
        prompts = [prompt for idx, prompt in enumerate(model.trained_words) if idx in pids]
    if user_prompt:
        prompts.append(user_prompt)
    prompts.append(model.prompt(weight))
    prompts = ', '.join(prompts).replace('\\', '\\\\').strip()
    prompts = clean_prompt(prompts)
    if not negative_prompt:
        return f'\n# Download URL: {model.download_url}\n{name}: >-\n  {prompts}\n'
    negative_prompt = clean_prompt(negative_prompt)
    return f'\n# Download URL: {model.download_url}\n{name}:\n  - >-\n    {prompts}\n  - {negative_prompt}\n'

def clean_prompt(prompt):
    blacklist = []
    if 'prompts_blacklist' in c.database:
        blacklist = c.database['prompts_blacklist']
        if not isinstance(blacklist, list):
            print('[ERROR] Blacklist should be a list')
            blacklist = []

    for blacklisted_prompt in blacklist:
        prompt = prompt.replace(blacklisted_prompt, '')

    prompt = prompt.replace(',', ', ')
    while '  ' in prompt: prompt = prompt.replace('  ', ' ')
    while ', ,' in prompt: prompt = prompt.replace(', ,', ',')
    while ',,' in prompt: prompt = prompt.replace(',,', ',')
    if prompt.startswith(', '): prompt = prompt[2:]

    return prompt
