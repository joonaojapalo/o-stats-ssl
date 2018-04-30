import os
import glob

__all__ = ["FileRepository"]


class FileRepository:
	def __init__(self, rootpath, year):
		self.basepath = os.path.join(rootpath, str(year))

	def get_html_base(self):
		return os.path.join(self.basepath, "competition_html")

	def get_html_paths(self):
		return glob.glob(os.path.join(self.get_html_base(), "*.*"))

	def get_calendar_html_path(self):
		return os.path.join(self.basepath, "cal", "cal.html")

	def get_competition_db_path(self):
		return os.path.join(self.basepath, "competitions.db3")

	def get_fetched_htmls_journal_file_path(self):
		return os.path.join(self.basepath, "competition_html.journal")

	def ensure_directory_layout(self):
		try:
			for d in ["cal", "competition_html"]:
				os.makedirs(os.path.join(self.basepath, d))
			return True
		except:
			return False
