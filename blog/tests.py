
from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category


class TestView(TestCase):
	def setUp(self) -> None:
		self.client=Client()
		self.user_trump=User.objects.create_user(username='trump',password='12345678')
		self.user_biden=User.objects.create_user(username='biden',password='12345678')
		self.category_programming=Category.objects.create(name='programming',slug='programming')
		self.category_music=Category.objects.create(name='music',slug='music')


		post_001=Post.objects.create(
			title='첫 번째 포스트입니다',
			content='hello',
			category=self.category_programming,
			author=self.user_trump
		)
		post_002=Post.objects.create(
			title='두 번째 포스트입니다',
			content='world',
			category=self.category_music,
			author=self.user_biden
		)
		post_003=Post.objects.create(
			title='세 번째 포스트입니다',
			content='!',
			author=self.user_biden
		)


		def category_card_test(self,soup)->None:
			categories_card=soup.find('div',id='categories-card')
			self.assertIn('Categories',categories_card.text)
			self.assertIn(f'{self.category_programming.name}({self.category_programming.post_set.count()})',categories_card.text)
			self.assertIn(f'{self.category_music.name}({self.category_miusic.post_set.count()})',categories_card.text)
			self.assertIn(f'미분류 (1)',categories_card.text)


	def navbar_test(self,soup):
		navbar=soup.nav
		self.assertIn('Blog',navbar.text)
		self.assertIn('About Me',navbar.text)


		logo_btn=navbar.find('a',text='Do it Django')
		self.assertEqual(logo_btn.attrs['href'],'/')
		home_btn=navbar.find('a',text='Home')
		self.assertEqual(home_btn.attrs['href'],'/')
		blog_btn=navbar.find('a',text='Blog')
		self.assertEqual(blog_btn.attrs['href'],'/blog/')
		about_me_btn=navbar.find('a',text='About Me')
		self.assertEqual(about_me_btn.attrs['href'],'/about_me/')
		


	def test_post_list(self):
		#포스트가 있는 경우
		self.assertEqual(Post.objects.count(), 3)
		
		
		response = self.client.get('/blog/')
		self.assertEqual(response.status_code, 200)
		soup=BeautifulSoup(response.content, 'html.parser')
		
		
		self.navbar_test(soup)
		self.category_card_test(soup)

		
		main_area=soup.find('div',id='main-area')
		self.assertIn('아직 게시물이 없습니다',main_area.text)


		post_001_card=main_area.find('div',id='post-1')
		self.assertIn(self.post_001.title, post_001_card.text)
		self.assertIn(self.post_001.category.name, post_001_card.text)
		post_002_card=main_area.find('div',id='post-2')
		self.assertIn(self.post_002.title, post_002_card.text)
		self.assertIn(self.post_002.category.name, post_002_card.text)
		post_003_card=main_area.find('div',id='post-3')
		self.assertIn('미분류', post_001_card.text)
		self.assertIn(self.post_003.category.name, post_003_card.text)
		self.assertIn(self.user_trump.username, main_area.text)
		self.assertIn(self.user_biden.username, main_area.text)


		#포스트가 없는 경우
		Post.objects.all().delete()
		self.assertEqual(Post.objects.count(), 0)
		response=self.client.get('/blog/')
		soup=BeautifulSoup(response.content, 'html.parser')
		main_area=soup.find('div',id='main-area')
		self.assertIn('아직 게시물이 없습니다', main_area.text)


	def test_post_detail(self):
		self.assertEqual(self.post_001.get_absolute_url(), '/blog/4/')
		

		#2 첫 번째 포스트의 상세 페이지 테스트
		#2.1 첫번째 post url로 접근하면 정상적으로 작동된다
		response=self.client.get(self.post_001.get_absolute_url())
		self.assertEqual(response.status_code, 200)
		soup=BeautifulSoup(response.content, 'html.parser')
		self.category_card_test(soup)
		#2.2 포스트 목록 페이지와 똑같은 네비게이션 바가 있다.
		navbar=soup.nav
		self.assertIn('Blog',navbar.text)
		self.assertIn('About Me',navbar.text)
		#2.3 첫 번째 포스트의 제목이 웹 브라우저 탭 타이틀에 들어있다.
		self.assertIn(self.post_001.title,soup.title.text)
		#2.4 첫 번째 포스트의 제목이 포스트 영역에 있다.
		main_area=soup.find('div',id='main-area')
		post_area=main_area.find('article', id='post-area')
		self.assertIn(self.category_programming.name,post_area.text)
		self.assertIn(self.post_001.title,post_area.text)
		#2.5 첫 번째 포스트의 작성자가 포스트 영역에 있다.
		self.assertIn(self.user_biden.username, post_area.text)
		#2.6 첫 번째 포스트의 내용이 포스트 영역에 있다.
		self.assertIn(self.post_001.content,post_area.text)
		#네비게이션 바 테스트
		self.navbar_test(soup)