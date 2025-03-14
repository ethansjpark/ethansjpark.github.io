// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-about",
    title: "about",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-gallery",
          title: "gallery",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/gallery/index.html";
          },
        },{id: "nav-publications",
          title: "publications",
          description: "publications by categories in reversed chronological order.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/publications/";
          },
        },{id: "nav-projects",
          title: "projects",
          description: "Collection of inspirational projects",
          section: "Navigation",
          handler: () => {
            window.location.href = "/projects/";
          },
        },{id: "post-youth",
      
        title: "youth",
      
      description: "trace from Kyoto",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2025/youth/";
        
      },
    },{id: "post-a-second",
      
        title: "a second",
      
      description: "footsteps from Tokyo",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2025/asc/";
        
      },
    },{id: "post-torii",
      
        title: "torii",
      
      description: "trace from Kyoto",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2025/tor/";
        
      },
    },{id: "post-kiss",
      
        title: "kiss",
      
      description: "heart of the empire state, New York",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2025/kiss/";
        
      },
    },{id: "post-silent-glow",
      
        title: "silent glow",
      
      description: "footsteps from Tokyo",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2025/sg/";
        
      },
    },{id: "post-structured-harmony",
      
        title: "structured harmony",
      
      description: "Atlanta, city of history",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2025/sh/";
        
      },
    },{id: "post-pathways-of-time",
      
        title: "pathways of time",
      
      description: "footsteps from Tokyo",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2025/pot/";
        
      },
    },{id: "post-clouded-serenity",
      
        title: "clouded serenity",
      
      description: "trace from Kyoto",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2025/cs/";
        
      },
    },{id: "post-time-surrounded-by-woods",
      
        title: "time surrounded by woods",
      
      description: "footsteps from Tokyo",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2025/tsbw/";
        
      },
    },{id: "post-solitude",
      
        title: "solitude",
      
      description: "Chicago after sunset",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2025/so/";
        
      },
    },{id: "post-flame",
      
        title: "flame",
      
      description: "Chicago after sunset",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2025/f/";
        
      },
    },{id: "post-eternal-watch",
      
        title: "eternal watch",
      
      description: "footsteps from Tokyo",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2025/etw/";
        
      },
    },{id: "post-circles",
      
        title: "circles",
      
      description: "footsteps from Tokyo",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2025/ci/";
        
      },
    },{id: "post-hand",
      
        title: "hand",
      
      description: "footsteps from Tokyo",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2025/h/";
        
      },
    },{id: "post-cosmo",
      
        title: "cosmo",
      
      description: "footsteps from Tokyo",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2025/c/";
        
      },
    },{id: "post-doors-to-the-beyond",
      
        title: "doors to the beyond",
      
      description: "footsteps from Tokyo",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2025/dttb/";
        
      },
    },{id: "post-roof-of-shadow",
      
        title: "roof of shadow",
      
      description: "trace from Kyoto",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2024/ros/";
        
      },
    },{id: "post-summer-flower",
      
        title: "summer flower",
      
      description: "trace from Kyoto",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2024/sf/";
        
      },
    },{id: "post-in-warmth",
      
        title: "in warmth",
      
      description: "trace from Kyoto",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2024/iw/";
        
      },
    },{id: "post-balloon",
      
        title: "balloon",
      
      description: "heart of the empire state, New York",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2024/ba/";
        
      },
    },{id: "post-contrast",
      
        title: "contrast",
      
      description: "footsteps from Tokyo",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2024/ct/";
        
      },
    },{id: "books-the-godfather",
          title: 'The Godfather',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the_godfather/";
            },},{id: "news-a-simple-inline-announcement",
          title: 'A simple inline announcement.',
          description: "",
          section: "News",},{id: "news-a-long-announcement-with-details",
          title: 'A long announcement with details',
          description: "",
          section: "News",handler: () => {
              window.location.href = "/news/announcement_2/";
            },},{id: "news-a-simple-inline-announcement-with-markdown-emoji-sparkles-smile",
          title: 'A simple inline announcement with Markdown emoji! :sparkles: :smile:',
          description: "",
          section: "News",},{id: "projects-medi",
          title: 'MEDi',
          description: "💊 AI-driven medication detection platform",
          section: "Projects",handler: () => {
              window.location.href = "/projects/1_project/";
            },},{id: "projects-thirdeye",
          title: 'ThirdEye',
          description: "📸 AI-Powered Motion Detection for Visually Impaired Athletes",
          section: "Projects",handler: () => {
              window.location.href = "/projects/2_project/";
            },},{
        id: 'social-email',
        title: 'email',
        section: 'Socials',
        handler: () => {
          window.open("mailto:%65%74%68%61%6E%73%6A%70%61%72%6B@%67%6D%61%69%6C.%63%6F%6D", "_blank");
        },
      },{
        id: 'social-github',
        title: 'GitHub',
        section: 'Socials',
        handler: () => {
          window.open("https://github.com//ethansjpark", "_blank");
        },
      },{
        id: 'social-linkedin',
        title: 'LinkedIn',
        section: 'Socials',
        handler: () => {
          window.open("https://www.linkedin.com/in//ethansjpark/", "_blank");
        },
      },{
      id: 'light-theme',
      title: 'Change theme to light',
      description: 'Change the theme of the site to Light',
      section: 'Theme',
      handler: () => {
        setThemeSetting("light");
      },
    },
    {
      id: 'dark-theme',
      title: 'Change theme to dark',
      description: 'Change the theme of the site to Dark',
      section: 'Theme',
      handler: () => {
        setThemeSetting("dark");
      },
    },
    {
      id: 'system-theme',
      title: 'Use system default theme',
      description: 'Change the theme of the site to System Default',
      section: 'Theme',
      handler: () => {
        setThemeSetting("system");
      },
    },];
