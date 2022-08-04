import imp
from turtle import pos
from unicodedata import name
from urllib import response
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
		#1.1 포스트 목록 페이지를 가져온다
		response = self.client.get('/blog/')
		#1.2 페이지가 로드된다
		self.assertEqual(response.status_code, 200)
		#1.3 페이지 타이틀은 'Blog'
		soup=BeautifulSoup(response.content, 'html.parser')
		self.assertEqual(soup.title.text, 'Blog\n')
		
		
		#2.1 메인 영역에 게시물이 하나도 없다면
		self.assertEqual(Post.objects.count(), 0)
		#2.2 '아직 게시물이 없습니다'
		main_area=soup.find('div',id='main-area')
		self.assertIn('아직 게시물이 없습니다',main_area.text)


		#3.1 게시물이 2개 있다면
		post_001=Post.objects.create(
			title='첫 번째 포스트입니다',
			content='hello',
			author=self.user_trump
		)
		post_002=Post.objects.create(
			title='.두 번째 포스트입니다',
			content='world',
			author=self.user_biden
		)
		self.assertEqual(Post.objects.count(),2)
		#3.2 포스트 목록 페이지를 새로고침했을 때
		response=self.client.get('/blog/')
		soup=BeautifulSoup(response.content, 'html.parser')
		self.assertEqual(response.status_code, 200)
		#3.3 메인 영역에 포스트 2개의 타이틀이 존재한다.
		main_area=soup.find('div',id='main-area')
		self.assertIn(post_001.title, main_area.text)
		self.assertIn(post_002.title, main_area.text)
		#3.4 '아직 게시물이 없습니다' 라는 문구는 더 이상 나타나지 않는다.
		self.assertNotIn('아직 게시물이 없습니다', main_area.text)
		self.assertIn(self.user_trump.username, main_area.text)
		self.assertIn(self.user_biden.username, main_area.text)
		#네비게이션 바 테스트
		self.navbar_test(soup)


	def test_post_detail(self):
		#1.1 포스트가 하나 있다.
		post_000=Post.objects.create(
			title='첫 번째 포스트입니다',
			content='hello',
			author=self.user_biden,
		)
		#1.2 페이지가 로드된다
		self.assertEqual(post_000.get_absolute_url(), '/blog/1/')
		

		#2 첫 번째 포스트의 상세 페이지 테스트
		#2.1 첫번째 post url로 접근하면 정상적으로 작동된다
		response=self.client.get(post_000.get_absolute_url())
		self.assertEqual(response.status_code, 200)
		soup=BeautifulSoup(response.content, 'html.parser')
		#2.2 포스트 목록 페이지와 똑같은 네비게이션 바가 있다.
		navbar=soup.nav
		self.assertIn('Blog',navbar.text)
		self.assertIn('About Me',navbar.text)
		#2.3 첫 번째 포스트의 제목이 웹 브라우저 탭 타이틀에 들어있다.
		self.assertIn(post_000.title,soup.title.text)
		#2.4 첫 번째 포스트의 제목이 포스트 영역에 있다.
		main_area=soup.find('div',id='main-area')
		post_area=main_area.find('article', id='post-area')
		self.assertIn(post_000.title,post_area.text)
		#2.5 첫 번째 포스트의 작성자가 포스트 영역에 있다.
		self.assertIn(self.user_biden.username, post_area.text)
		#2.6 첫 번째 포스트의 내용이 포스트 영역에 있다.
		self.assertIn(post_000.content,post_area.text)
		#네비게이션 바 테스트
		self.navbar_test(soup)