from django.shortcuts import redirect, render

from .models import Note


def home(request):
	if request.method == 'POST':
		content = request.POST.get('content', '').strip()
		if content:
			Note.objects.create(content=content)
		return redirect('home')

	notes = Note.objects.order_by('-id')
	return render(request, 'notes/home.html', {'notes': notes})
